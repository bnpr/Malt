#include <string>
#include <map>
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
struct preprocessor_directive : seq<STRING("#"), until<eol, any>> {};
struct META;
struct _s_ : star<not_at<META>, sor<line_comment, multiline_comment, preprocessor_directive, space>> {};

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

struct _ms_ : star<space> {};
struct META_PROP_VALUE : star<not_at<one<';'>>, any> {};
struct META_PROP : seq<not_at<one<'@'>>, IDENTIFIER, _ms_, one<'='>, _ms_, META_PROP_VALUE, _ms_, one<';'>> {};
struct META_PROPS : plus<seq<_ms_, META_PROP, _ms_>> {};
struct META_MEMBER : seq<one<'@'>, _ms_, IDENTIFIER, _ms_, one<':'>, META_PROPS> {};
struct META_MEMBERS : plus<seq<_ms_, META_MEMBER, _ms_>> {};
struct META : seq<STRING("/*"), _ms_, STRING("META"), _ms_, META_MEMBERS, _ms_, STRING("*/")> {};

struct MEMBER : seq<opt<PRECISION>, _s_, TYPE, _s_, IDENTIFIER, _s_, opt<ARRAY_SIZE>, _s_, END> {};
struct MEMBERS : plus<seq<_s_, MEMBER, _s_>> {};
struct STRUCT_DEF : seq<opt<META, _ms_>, STRUCT, _s_, IDENTIFIER, _s_, LBRACE, _s_, opt<MEMBERS>, _s_, RBRACE> {};

struct PARAMETER : seq<opt<IO>, _s_, opt<PRECISION>, _s_, TYPE, _s_, IDENTIFIER, _s_, opt<ARRAY_SIZE>> {};
struct PARAMETERS : list<seq<_s_, PARAMETER, _s_>, seq<_s_, COMMA, _s_>> {};
struct FUNCTION_SIG : seq<TYPE, _s_, IDENTIFIER, _s_, LPAREN, _s_, opt<PARAMETERS>, _s_, RPAREN> {}; 
struct FUNCTION_DEC : seq<opt<META, _ms_>, FUNCTION_SIG, _s_, LBRACE> {}; 

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
        META_PROP_VALUE,
        META_PROP,
        META_MEMBER,
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

std::map<std::string, rapidjson::Value> get_meta_dict(parse_tree::node* meta, rapidjson::MemoryPoolAllocator<>& allocator)
{
    using namespace rapidjson;
    std::map<std::string, Value> meta_dict = {};
    if(meta)
    {
        for(auto& meta_member : meta->children)
        {
            std::string member_name = std::string(get<IDENTIFIER>(meta_member.get())->string_view());
            Value member_meta = Value(kObjectType);
            
            for(auto& meta_prop : meta_member->children)
            {
                if(!meta_prop->is_type<META_PROP>())
                {
                    continue; //Other type of child
                }
                std::string prop_name = std::string(get<IDENTIFIER>(meta_prop.get())->string_view());
                std::string prop_value = std::string(get<META_PROP_VALUE>(meta_prop.get())->string_view());
                member_meta.AddMember(
                    Value(prop_name.c_str(), allocator), Value(prop_value.c_str(), allocator), allocator
                );
            }
            
            meta_dict[member_name] = member_meta;
        }
    }
    return meta_dict;
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

            parse_tree::node* meta = get<META>(child.get());
            auto meta_dict = get_meta_dict(meta, json.GetAllocator());

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
                
                if(meta_dict.count(name))
                {
                    member_def.AddMember("meta", meta_dict[name], json.GetAllocator());
                }
                else
                {
                    member_def.AddMember("meta", Value(kObjectType), json.GetAllocator());
                }

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

            parse_tree::node* meta = get<META>(child.get());
            auto meta_dict = get_meta_dict(meta, json.GetAllocator());

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
                
                if(meta_dict.count(name))
                {
                    parameter_dec.AddMember("meta", meta_dict[name], json.GetAllocator());
                }
                else
                {
                    parameter_dec.AddMember("meta", Value(kObjectType), json.GetAllocator());
                }

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

