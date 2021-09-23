#include <string>
#include <iostream>

#include <tao/pegtl.hpp>
#include <tao/pegtl/contrib/analyze.hpp>
#include <tao/pegtl/contrib/trace.hpp>
#include <tao/pegtl/contrib/parse_tree.hpp>
#include <tao/pegtl/contrib/parse_tree_to_dot.hpp>

#include <rapidjson/document.h>
#include "rapidjson/prettywriter.h"

using namespace tao::pegtl;

#define STRING(string) TAO_PEGTL_STRING(string)
#define ISTRING(string) TAO_PEGTL_ISTRING(string)
#define KEYWORD(string) TAO_PEGTL_KEYWORD(string)

struct line_comment : seq<STRING("//"), until<eol, any>> {};
struct multiline_comment : seq<STRING("/*"), until<STRING("*/"), any>> {};
struct _s_ : star<sor<line_comment, multiline_comment, space>> {};

struct LPAREN : one<'('> {};
struct RPAREN : one<')'> {};
struct LBRACE : one<'{'> {};
struct RBRACE : one<'}'> {};
struct LBRACKET : one<'['> {};
struct RBRACKET : one<']'> {};
struct COMMA : one<','> {};
struct END : one<';'> {};
struct STRUCT : KEYWORD("struct") {};
struct IDENTIFIER : identifier {};
struct TYPE : identifier {};
struct DIGITS : plus<digit> {};
struct PRECISION : sor<KEYWORD("lowp"), KEYWORD("mediump"), KEYWORD("highp")> {};
struct IO : sor<KEYWORD("in"), KEYWORD("out"), KEYWORD("inout")> {};
struct ARRAY_SIZE : seq<LBRACKET, _s_, DIGITS, _s_, RBRACKET> {};

struct FILE_PATH : plus<not_one<'"'>> {};
struct QUOTED_FILE_PATH : seq<one<'"'>, FILE_PATH, one<'"'>> {};
struct LINE_DIRECTIVE : seq<STRING("#line"), _s_, DIGITS, _s_, QUOTED_FILE_PATH> {};

struct PAREN_SCOPE;
struct PAREN_SCOPE : seq<LPAREN, until<RPAREN, sor<PAREN_SCOPE, any>>> {};
struct META_PROP : seq<IDENTIFIER, _s_, PAREN_SCOPE> {};
struct META_PROPS : list<seq<_s_, META_PROP, _s_>, seq<_s_, COMMA, _s_>> {};
struct META : seq<STRING("META"), _s_, LPAREN, LPAREN, META_PROPS, RPAREN, RPAREN> {};

struct MEMBER : seq<opt<PRECISION>, _s_, TYPE, _s_, IDENTIFIER, _s_, opt<ARRAY_SIZE>, _s_, opt<META>, _s_, END> {};
struct MEMBERS : plus<seq<_s_, MEMBER, _s_>> {};
struct STRUCT_DEF : seq<STRUCT, _s_, IDENTIFIER, _s_, LBRACE, _s_, opt<MEMBERS>, _s_, RBRACE> {};

struct PARAMETER : seq<opt<IO>, _s_, opt<PRECISION>, _s_, TYPE, _s_, IDENTIFIER, _s_, opt<ARRAY_SIZE>, _s_, opt<META>> {};
struct PARAMETERS : list<seq<_s_, PARAMETER, _s_>, seq<_s_, COMMA, _s_>> {};
struct FUNCTION_SIG : seq<TYPE, _s_, IDENTIFIER, _s_, LPAREN, _s_, opt<PARAMETERS>, _s_, RPAREN> {}; 
struct FUNCTION_DEC : seq<FUNCTION_SIG, _s_, LBRACE> {}; 

struct GLSL_GRAMMAR : star<sor<LINE_DIRECTIVE, STRUCT_DEF, FUNCTION_DEC, any>> {};

template<typename Rule>
using selector = parse_tree::selector
<
    Rule,
    parse_tree::store_content::on
    <
        IDENTIFIER,
        TYPE,
        DIGITS,
        PRECISION,
        IO,
        ARRAY_SIZE,
        FILE_PATH,
        PAREN_SCOPE,
        META_PROP,
        META,
        MEMBER,
        MEMBERS,
        STRUCT_DEF,
        PARAMETER,
        PARAMETERS,
        FUNCTION_SIG,
        FUNCTION_DEC
    >
>;

void print_nodes(parse_tree::node& node)
{
    if(node.has_content())
    {
        std::cout << node.type << " : " << node.string_view() << std::endl;
    }
    
    for(auto& child : node.children)
    {
        if(child)
        {
            print_nodes(*child);
        }
    }
}

template<typename T>
parse_tree::node* get(parse_tree::node* parent)
{
    for(auto& child : parent->children)
    {
        if(child->is_type<T>())
        {
            return child.get();
        }
    }
    return nullptr;
}

std::string remove_extra_whitespace(const std::string& str)
{
    int len = str.length();
	std::string result;
    result.reserve(len);
    bool was_space = false;
    for(int i=0; i < len; i++)
    {
        bool is_space = isspace(str[i]);
        if(is_space)
        {
            if(!was_space) result += " ";
        }
        else
        {
            result += str[i];
        }
        was_space = is_space;
    }
    return result;
}

int main(int argc, char* argv[])
{
    if(argc < 2) return 1;
    const char* path = argv[1];

    file_input input(path);
    
    #ifdef _DEBUG
    {
        const std::size_t issues = analyze<GLSL_GRAMMAR>();
        if(issues) return issues;
    }
    #endif

    //standard_trace<GLSL_GRAMMAR>(input);
    //input.restart();
    
    auto root = parse_tree::parse<GLSL_GRAMMAR, selector>(input);
    input.restart();
    if(!root) return 1;

    //print_nodes(*root);
    //parse_tree::print_dot(std::cout, *root);

    using namespace rapidjson;

    Document json;
    json.Parse("{}");
    json.AddMember("structs", Value(kObjectType), json.GetAllocator());
    Value& structs = json["structs"];
    json.AddMember("functions", Value(kObjectType), json.GetAllocator());
    Value& functions = json["functions"];

    std::string current_file = "";

    for(auto& child : root->children)
    {
        if(child->is_type<FILE_PATH>())
        {
            current_file = std::string(child->string_view());
        }
        else if(child->is_type<STRUCT_DEF>())
        {
            std::string name = std::string(get<IDENTIFIER>(child.get())->string_view());
            
            structs.AddMember(Value(name.c_str(), json.GetAllocator()), Value(kObjectType), json.GetAllocator());
            Value& struct_def = structs[name.c_str()];
            struct_def.AddMember("name", Value(name.c_str(), json.GetAllocator()), json.GetAllocator());
            struct_def.AddMember("file", Value(current_file.c_str(), json.GetAllocator()), json.GetAllocator());
            struct_def.AddMember("members", Value(kArrayType), json.GetAllocator());
            Value& members_array = struct_def["members"];

            parse_tree::node* members = get<MEMBERS>(child.get());
            if(!members) continue;

            for(auto& member : members->children)
            {
                std::string name = std::string(get<IDENTIFIER>(member.get())->string_view());
                std::string type = std::string(get<TYPE>(member.get())->string_view());
                int array_size = 0;
                
                parse_tree::node* array_size_node = get<ARRAY_SIZE>(member.get());
                if(array_size_node)
                {
                    std::string size = std::string(get<DIGITS>(array_size_node)->string_view());
                    array_size = std::stoi(size);
                }

                Value member_def = Value(kObjectType);
                member_def.AddMember("name", Value(name.c_str(), json.GetAllocator()), json.GetAllocator());
                member_def.AddMember("type", Value(type.c_str(), json.GetAllocator()), json.GetAllocator());
                member_def.AddMember("size", Value(array_size), json.GetAllocator());
                Value meta_dic = Value(kObjectType);
                parse_tree::node* meta = get<META>(member.get());
                if(meta)
                {
                    for(auto& meta_prop : meta->children)
                    {
                        std::string name = std::string(get<IDENTIFIER>(meta_prop.get())->string_view());
                        std::string value = std::string(get<PAREN_SCOPE>(meta_prop.get())->string_view());
                        meta_dic.AddMember(Value(name.c_str(), json.GetAllocator()), Value(value.c_str(), json.GetAllocator()), json.GetAllocator());
                    }
                }
                member_def.AddMember("meta", meta_dic, json.GetAllocator());
                members_array.PushBack(member_def, json.GetAllocator());
            }
        }
        else if(child->is_type<FUNCTION_DEC>())
        {
            parse_tree::node* signature = get<FUNCTION_SIG>(child.get());
            std::string name = std::string(get<IDENTIFIER>(signature)->string_view());
            std::string signature_str = std::string(signature->string_view());
            signature_str = remove_extra_whitespace(signature_str);
            std::string key_name = name;
            if(functions.HasMember(key_name.c_str()))
            {
                key_name += " - " + signature_str;
            }
            std::string type = std::string(get<TYPE>(signature)->string_view());
            
            functions.AddMember(Value(key_name.c_str(), json.GetAllocator()), Value(kObjectType), json.GetAllocator());
            Value& function_dec = functions[key_name.c_str()];
            function_dec.AddMember("name", Value(name.c_str(), json.GetAllocator()), json.GetAllocator());
            function_dec.AddMember("type", Value(type.c_str(), json.GetAllocator()), json.GetAllocator());
            function_dec.AddMember("file", Value(current_file.c_str(), json.GetAllocator()), json.GetAllocator());
            function_dec.AddMember("signature", Value(signature_str.c_str(), json.GetAllocator()), json.GetAllocator());
            function_dec.AddMember("parameters", Value(kArrayType), json.GetAllocator());
            Value& parameters_array = function_dec["parameters"];

            parse_tree::node* parameters = get<PARAMETERS>(signature);
            if(!parameters) continue;

            for(auto& parameter : parameters->children)
            {
                std::string name = std::string(get<IDENTIFIER>(parameter.get())->string_view());
                std::string type = std::string(get<TYPE>(parameter.get())->string_view());
                std::string io = "in";
                int array_size = 0;
                
                parse_tree::node* array_size_node = get<ARRAY_SIZE>(parameter.get());
                if(array_size_node)
                {
                    std::string size = std::string(get<DIGITS>(array_size_node)->string_view());
                    array_size = std::stoi(size);
                }
                
                parse_tree::node* io_node = get<IO>(parameter.get());
                if(io_node)
                {
                    io = std::string(io_node->string_view());
                }

                Value parameter_dec = Value(kObjectType);
                parameter_dec.AddMember("name", Value(name.c_str(), json.GetAllocator()), json.GetAllocator());
                parameter_dec.AddMember("type", Value(type.c_str(), json.GetAllocator()), json.GetAllocator());
                parameter_dec.AddMember("size", Value(array_size), json.GetAllocator());
                parameter_dec.AddMember("io", Value(io.c_str(), json.GetAllocator()), json.GetAllocator());
                Value meta_dic = Value(kObjectType);
                parse_tree::node* meta = get<META>(parameter.get());
                if(meta)
                {
                    for(auto& meta_prop : meta->children)
                    {
                        std::string name = std::string(get<IDENTIFIER>(meta_prop.get())->string_view());
                        std::string value = std::string(get<PAREN_SCOPE>(meta_prop.get())->string_view());
                        meta_dic.AddMember(Value(name.c_str(), json.GetAllocator()), Value(value.c_str(), json.GetAllocator()), json.GetAllocator());
                    }
                }
                parameter_dec.AddMember("meta", meta_dic, json.GetAllocator());
                parameters_array.PushBack(parameter_dec, json.GetAllocator());
            }
        }
    }

    StringBuffer result;
    PrettyWriter<StringBuffer> writer(result);
    json.Accept(writer);

    std::cout << result.GetString();

    return 0;
}

