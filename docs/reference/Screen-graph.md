# Screen Graph Reference
---
## Input
---
### **Geometry**
- **Inputs**  
	- **Space** *: ( int | ENUM(Object,World,Camera,Screen) ) - default = 1*  
	- **IOR** *: ( float ) - default = 1.45*  
- **Outputs**  
	- **Position** *: ( vec3 )*  
	- **Incoming** *: ( vec3 )*  
	- **Normal** *: ( vec3 ) - default = NORMAL*  
	- **True Normal** *: ( vec3 )*  
	- **Is Backfacing** *: ( bool )*  
	- **Facing** *: ( float )*  
	- **Fresnel** *: ( float )*  
	- **Reflection** *: ( vec3 )*  
	- **Refraction** *: ( vec3 )*  
---
### **Tangent**
---
#### **Radial**
- **Inputs**  
	- **Axis** *: ( int | ENUM(X,Y,Z) ) - default = 2*  
	- **Object Space** *: ( bool ) - default = True*  
- **Outputs**  
	- **Tangent** *: ( vec3 )*  
	- **Bitangent** *: ( vec3 )*  
---
#### **Procedural UV**
- **Inputs**  
	- **Uv** *: ( vec2 )*  
- **Outputs**  
	- **Tangent** *: ( vec3 )*  
	- **Bitangent** *: ( vec3 )*  
---
### **Id**
- **Outputs**  
	- **Object Id** *: ( vec4 )*  
	- **Custom Id A** *: ( vec4 )*  
	- **Custom Id B** *: ( vec4 )*  
	- **Custom Id C** *: ( vec4 )*  
---
### **Camera Data**
- **Outputs**  
	- **View Direction** *: ( vec3 )*  
	- **Screen UV** *: ( vec2 )*  
	- **Z Depth** *: ( float )*  
	- **View Distance** *: ( float )*  
	- **Camera Position** *: ( vec3 )*  
	- **Camera Matrix** *: ( mat4 )*  
	- **Projection Matrix** *: ( mat4 )*  
	- **Is Orthographic** *: ( bool )*  
---
### **Render Info**
- **Outputs**  
	- **Resolution** *: ( vec2 )*  
	- **Current Sample** *: ( int )*  
	- **Sample Offset** *: ( vec2 )*  
---
### **Time Info**
- **Outputs**  
	- **Time** *: ( float )*  
	- **Frame** *: ( int )*  
---
### **Random**
- **Inputs**  
	- **Seed** *: ( float )*  
- **Outputs**  
	- **Per Object** *: ( vec4 )*  
	- **Per Sample** *: ( vec4 )*  
	- **Per Pixel** *: ( vec4 )*  
---
## Parameters
---
### **Boolean**
- **Inputs**  
	- **B** *: ( bool )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **Float**
- **Inputs**  
	- **F** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **Integer**
- **Inputs**  
	- **I** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
### **Vector 2D**
- **Inputs**  
	- **V** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
### **Vector 3D**
- **Inputs**  
	- **V** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **Vector 4D**
- **Inputs**  
	- **V** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **RGB Color**
- **Inputs**  
	- **V** *: ( vec3 | Color )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **RGBA Color**
- **Inputs**  
	- **V** *: ( vec4 | Color )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **Color Ramp**
- **Inputs**  
	- **Color Ramp** *: ( sampler1D )*  
- **Outputs**  
	- **result** *: ( sampler1D )*  
---
### **Image**
- **Inputs**  
	- **Image** *: ( sampler2D )*  
- **Outputs**  
	- **result** *: ( sampler2D )*  
---
## Math
---
### **Hash**
- **Inputs**  
	- **V** *: ( vec4 | Data )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **Quaternion**
---
#### **From Axis Angle**
- **Inputs**  
	- **Axis** *: ( vec3 | Normal )*  
	- **Angle** *: ( float | Angle )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **From Vector Delta**
- **Inputs**  
	- **From** *: ( vec3 | Normal )*  
	- **To** *: ( vec3 | Normal )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Inverted**
- **Inputs**  
	- **Q** *: ( vec4 | Quaternion ) - default = (0.0, 0.0, 0.0, 1.0)*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Multiply**
- **Inputs**  
	- **A** *: ( vec4 | Quaternion ) - default = (0.0, 0.0, 0.0, 1.0)*  
	- **B** *: ( vec4 | Quaternion ) - default = (0.0, 0.0, 0.0, 1.0)*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Transform**
- **Inputs**  
	- **Q** *: ( vec4 | Quaternion ) - default = (0.0, 0.0, 0.0, 1.0)*  
	- **Vector** *: ( vec3 | Vector ) - default = (0.0, 0.0, 0.0)*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Mix**
- **Inputs**  
	- **A** *: ( vec4 | Quaternion ) - default = (0.0, 0.0, 0.0, 1.0)*  
	- **B** *: ( vec4 | Quaternion ) - default = (0.0, 0.0, 0.0, 1.0)*  
	- **Factor** *: ( float | Slider ) - default = 0.5*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **Matrix**
---
#### **From Translation**
- **Inputs**  
	- **T** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( mat4 )*  
---
#### **From Quaternion**
- **Inputs**  
	- **Q** *: ( vec4 | Quaternion ) - default = (0.0, 0.0, 0.0, 1.0)*  
- **Outputs**  
	- **result** *: ( mat4 )*  
---
#### **From Euler**
- **Inputs**  
	- **E** *: ( vec3 | Euler )*  
- **Outputs**  
	- **result** *: ( mat4 )*  
---
#### **From Scale**
- **Inputs**  
	- **S** *: ( vec3 | Vector ) - default = (1.0, 1.0, 1.0)*  
- **Outputs**  
	- **result** *: ( mat4 )*  
---
#### **Is Orthographic**
- **Inputs**  
	- **Matrix** *: ( mat4 ) - default = mat4(1)*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Inverse**
- **Inputs**  
	- **Matrix** *: ( mat4 ) - default = mat4(1)*  
- **Outputs**  
	- **result** *: ( mat4 )*  
---
#### **Multiply**
- **Inputs**  
	- **A** *: ( mat4 ) - default = mat4(1)*  
	- **B** *: ( mat4 ) - default = mat4(1)*  
- **Outputs**  
	- **result** *: ( mat4 )*  
---
### **Boolean Logic**
---
#### **And**
- **Inputs**  
	- **A** *: ( bool )*  
	- **B** *: ( bool )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Or**
- **Inputs**  
	- **A** *: ( bool )*  
	- **B** *: ( bool )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Not**
- **Inputs**  
	- **B** *: ( bool )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Equal**
- **Inputs**  
	- **A** *: ( bool )*  
	- **B** *: ( bool )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Not Equal**
- **Inputs**  
	- **A** *: ( bool )*  
	- **B** *: ( bool )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **If Else**
- **Inputs**  
	- **Condition** *: ( bool )*  
	- **If True** *: ( bool )*  
	- **If False** *: ( bool )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
### **Float**
---
#### **Add**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Subtract**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Multiply**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Divide**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Map Range**
- **Inputs**  
	- **Clamped** *: ( bool ) - default = True*  
	- **Value** *: ( float ) - default = 0.5*  
	- **From Min** *: ( float )*  
	- **From Max** *: ( float ) - default = 1.0*  
	- **To Min** *: ( float )*  
	- **To Max** *: ( float ) - default = 1.0*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Modulo**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Power**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Square Root**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Round**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Fractional Part**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Floor**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Ceil**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Clamp**
- **Inputs**  
	- **A** *: ( float )*  
	- **Min** *: ( float )*  
	- **Max** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Sign**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Absolute**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Minimum**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Maximum**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Mix**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
	- **Fac** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Sine**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Cosine**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Tangent**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Arcsine**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Arcosine**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Arctangent**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Radians to Degrees**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Degrees to Radians**
- **Inputs**  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Equal**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
	- **E** *: ( float ) - default = 0.1*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Not Equal**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
	- **E** *: ( float ) - default = 0.1*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Greater**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Greater or Equal**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Less**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Less or Equal**
- **Inputs**  
	- **A** *: ( float )*  
	- **B** *: ( float )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **If Else**
- **Inputs**  
	- **Condition** *: ( bool )*  
	- **If True** *: ( float )*  
	- **If False** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **Integer**
---
#### **Add**
- **Inputs**  
	- **A** *: ( int )*  
	- **B** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
#### **Subtract**
- **Inputs**  
	- **A** *: ( int )*  
	- **B** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
#### **Multiply**
- **Inputs**  
	- **A** *: ( int )*  
	- **B** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
#### **Divide**
- **Inputs**  
	- **A** *: ( int )*  
	- **B** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
#### **Modulo**
- **Inputs**  
	- **A** *: ( int )*  
	- **B** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
#### **Clamp**
- **Inputs**  
	- **A** *: ( int )*  
	- **Min** *: ( int )*  
	- **Max** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
#### **Sign**
- **Inputs**  
	- **A** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
#### **Absolute**
- **Inputs**  
	- **A** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
#### **Minimum**
- **Inputs**  
	- **A** *: ( int )*  
	- **B** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
#### **Maximum**
- **Inputs**  
	- **A** *: ( int )*  
	- **B** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
#### **Equal**
- **Inputs**  
	- **A** *: ( int )*  
	- **B** *: ( int )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Not Equal**
- **Inputs**  
	- **A** *: ( int )*  
	- **B** *: ( int )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Greater**
- **Inputs**  
	- **A** *: ( int )*  
	- **B** *: ( int )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Greater or Equal**
- **Inputs**  
	- **A** *: ( int )*  
	- **B** *: ( int )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Less**
- **Inputs**  
	- **A** *: ( int )*  
	- **B** *: ( int )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Less or Equal**
- **Inputs**  
	- **A** *: ( int )*  
	- **B** *: ( int )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **If Else**
- **Inputs**  
	- **Condition** *: ( bool )*  
	- **If True** *: ( int )*  
	- **If False** *: ( int )*  
- **Outputs**  
	- **result** *: ( int )*  
---
### **Vector 2D**
---
#### **Add**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Subtract**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Multiply**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Divide**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Scale**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **Fac** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Map Range**
- **Inputs**  
	- **Clamped** *: ( bool ) - default = True*  
	- **UV** *: ( vec2 ) - default = vec2(0.5)*  
	- **From Min** *: ( vec2 ) - default = (0.0, 0.0)*  
	- **From Max** *: ( vec2 ) - default = (1.0, 1.0)*  
	- **To Min** *: ( vec2 ) - default = (0.0, 0.0)*  
	- **To Max** *: ( vec2 ) - default = (1.0, 1.0)*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Modulo**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Power**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Square Root**
- **Inputs**  
	- **A** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Distort**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
	- **Fac** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Round**
- **Inputs**  
	- **A** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Fraction**
- **Inputs**  
	- **A** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Floor**
- **Inputs**  
	- **A** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Ceil**
- **Inputs**  
	- **A** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Snap**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Clamp**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **Min** *: ( vec2 )*  
	- **Max** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Sign**
- **Inputs**  
	- **A** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Absolute**
- **Inputs**  
	- **A** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Min**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Max**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Mix 2D**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
	- **Factor** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Mix**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
	- **Fac** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Normalize**
- **Inputs**  
	- **A** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Length**
- **Inputs**  
	- **A** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Distance**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Dot Product**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Sine**
- **Inputs**  
	- **A** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Cosine**
- **Inputs**  
	- **A** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Tangent**
- **Inputs**  
	- **A** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Rotate**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **Angle** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Angle**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Equal**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Not Equal**
- **Inputs**  
	- **A** *: ( vec2 )*  
	- **B** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **If Else**
- **Inputs**  
	- **Condition** *: ( bool )*  
	- **If True** *: ( vec2 )*  
	- **If False** *: ( vec2 )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Combine**
- **Inputs**  
	- **X** *: ( float )*  
	- **Y** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec2 )*  
---
#### **Separate**
- **Inputs**  
	- **A** *: ( vec2 )*  
- **Outputs**  
	- **X** *: ( float )*  
	- **Y** *: ( float )*  
---
### **Vector 3D**
---
#### **Add**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Subtract**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Multiply**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Divide**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Scale**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **Fac** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Map Range**
- **Inputs**  
	- **Clamped** *: ( bool ) - default = True*  
	- **Vector** *: ( vec3 ) - default = vec3(0.5)*  
	- **From Min** *: ( vec3 | Vector ) - default = (0.0, 0.0, 0.0)*  
	- **From Max** *: ( vec3 | Vector ) - default = (1.0, 1.0, 1.0)*  
	- **To Min** *: ( vec3 | Vector ) - default = (0.0, 0.0, 0.0)*  
	- **To Max** *: ( vec3 | Vector ) - default = (1.0, 1.0, 1.0)*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Modulo**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Power**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Square Root**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Distort**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
	- **Fac** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Round**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Fraction**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Floor**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Ceil**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Snap**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Clamp**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **Min** *: ( vec3 | Vector )*  
	- **Max** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Sign**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Absolute**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Min**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Max**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Mix 3D**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
	- **Factor** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Mix**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
	- **Fac** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Normalize**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Length**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Distance**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Dot Product**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Cross Product**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Reflect**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Refract**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
	- **Ior** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Faceforward**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
	- **C** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Sine**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Cosine**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Tangent**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Rotate Euler**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **Euler** *: ( vec3 | Euler )*  
	- **Invert** *: ( bool )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Rotate Axis Angle**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **Axis** *: ( vec3 | Vector ) - default = (0.0, 0.0, 1.0)*  
	- **Angle** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Angle**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Equal**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Not Equal**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
	- **B** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **If Else**
- **Inputs**  
	- **Condition** *: ( bool )*  
	- **If True** *: ( vec3 | Vector )*  
	- **If False** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Combine**
- **Inputs**  
	- **X** *: ( float )*  
	- **Y** *: ( float )*  
	- **Z** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Separate**
- **Inputs**  
	- **A** *: ( vec3 | Vector )*  
- **Outputs**  
	- **X** *: ( float )*  
	- **Y** *: ( float )*  
	- **Z** *: ( float )*  
---
### **Vector 4D**
---
#### **Add**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Subtract**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Multiply**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Divide**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Scale**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **Fac** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Map Range**
- **Inputs**  
	- **Clamped** *: ( bool ) - default = True*  
	- **Vector** *: ( vec4 ) - default = vec4(0.5)*  
	- **From Min** *: ( vec4 | Vector ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **From Max** *: ( vec4 | Vector ) - default = (1.0, 1.0, 1.0, 1.0)*  
	- **To Min** *: ( vec4 | Vector ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **To Max** *: ( vec4 | Vector ) - default = (1.0, 1.0, 1.0, 1.0)*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Modulo**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Power**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Square Root**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Distort**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
	- **Fac** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Round**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Fraction**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Floor**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Ceil**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Clamp**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **Min** *: ( vec4 | Vector )*  
	- **Max** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Sign**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Absolute**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Min**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Max**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Mix 4D**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
	- **Factor** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Mix**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
	- **Fac** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Normalize**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Length**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Distance**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Dot Product**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Sine**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Cosine**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Tangent**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Angle**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Equal**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Not Equal**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
	- **B** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( bool )*  
---
#### **Vec4 If Else**
- **Inputs**  
	- **Condition** *: ( bool )*  
	- **If True** *: ( vec4 | Vector )*  
	- **If False** *: ( vec4 | Vector )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Combine**
- **Inputs**  
	- **R** *: ( float )*  
	- **G** *: ( float )*  
	- **B** *: ( float )*  
	- **A** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Combine Color**
- **Inputs**  
	- **C** *: ( vec3 | Color )*  
	- **A** *: ( float | Slider ) - default = 1.0*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Separate**
- **Inputs**  
	- **A** *: ( vec4 | Vector )*  
- **Outputs**  
	- **R** *: ( float )*  
	- **G** *: ( float )*  
	- **B** *: ( float )*  
	- **A** *: ( float )*  
---
#### **Separate Color**
- **Inputs**  
	- **A** *: ( vec4 | Color )*  
- **Outputs**  
	- **C** *: ( vec3 )*  
	- **A** *: ( float )*  
---
## Vector
---
### **Surface Gradient From Normal**
- **Inputs**  
	- **Base Normal** *: ( vec3 | Normal ) - default = NORMAL*  
	- **Custom Normal** *: ( vec3 | Normal ) - default = NORMAL*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **Normal From Surface Gradient**
- **Inputs**  
	- **Base Normal** *: ( vec3 | Normal ) - default = NORMAL*  
	- **Surface Gradient** *: ( vec3 | Vector ) - default = (0.0, 0.0, 0.0)*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **Matrix**
---
#### **Transform Point**
- **Inputs**  
	- **Matrix** *: ( mat4 ) - default = mat4(1)*  
	- **Point** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Project Point**
- **Inputs**  
	- **Matrix** *: ( mat4 ) - default = mat4(1)*  
	- **Point** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Project Point To Screen Coordinates**
- **Inputs**  
	- **Matrix** *: ( mat4 ) - default = mat4(1)*  
	- **Point** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Transform Direction**
- **Inputs**  
	- **Matrix** *: ( mat4 ) - default = mat4(1)*  
	- **Direction** *: ( vec3 | Vector )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Transform Normal**
- **Inputs**  
	- **Matrix** *: ( mat4 ) - default = mat4(1)*  
	- **Normal** *: ( vec3 | Normal )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **Pixel Size in World Space**
- **Inputs**  
	- **Depth** *: ( float ) - default = pixel_depth()*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **Bevel**
---
#### **Soft Bevel**
- **Inputs**  
	- **Samples** *: ( int ) - default = 32*  
	- **Radius** *: ( float ) - default = 0.02*  
	- **Distribution Exponent** *: ( float ) - default = 2.0*  
	- **Only Self** *: ( bool )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Hard Bevel**
- **Inputs**  
	- **Samples** *: ( int ) - default = 32*  
	- **Radius** *: ( float ) - default = 0.01*  
	- **Max Dot** *: ( float ) - default = 0.75*  
	- **Only Self** *: ( bool )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **Transform**
- **Inputs**  
	- **Type** *: ( int | ENUM(Point,Vector,Normal) )*  
	- **From** *: ( int | ENUM(Object,World,Camera) )*  
	- **To** *: ( int | ENUM(Object,World,Camera,Screen) )*  
	- **Vector** *: ( vec3 | Vector )*  
- **Outputs**  
	- **Vector** *: ( vec3 | Vector )*  
---
### **Mapping**
---
#### **Point**
- **Inputs**  
	- **Vector** *: ( vec3 | Vector ) - default = vec3(0.0)*  
	- **Location** *: ( vec3 | Vector )*  
	- **Rotation** *: ( vec3 | Euler )*  
	- **Scale** *: ( vec3 | Vector ) - default = (1.0, 1.0, 1.0)*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Texture**
- **Inputs**  
	- **Vector** *: ( vec3 | Vector ) - default = vec3(0.0)*  
	- **Location** *: ( vec3 | Vector )*  
	- **Rotation** *: ( vec3 | Euler )*  
	- **Scale** *: ( vec3 | Vector ) - default = (1.0, 1.0, 1.0)*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Vector**
- **Inputs**  
	- **Vector** *: ( vec3 | Vector ) - default = vec3(0.0)*  
	- **Rotation** *: ( vec3 | Euler )*  
	- **Scale** *: ( vec3 | Vector ) - default = (1.0, 1.0, 1.0)*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Normal**
- **Inputs**  
	- **Vector** *: ( vec3 | Vector ) - default = vec3(0.0)*  
	- **Rotation** *: ( vec3 | Euler )*  
	- **Scale** *: ( vec3 | Vector ) - default = (1.0, 1.0, 1.0)*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
## Color
---
### **Alpha Blend**
Blends the blend color as a layer over the base color.

- **Inputs**  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	>The blend color.
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **Grayscale**
- **Inputs**  
	- **Color** *: ( vec3 )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **Linear To sRGB**
- **Inputs**  
	- **Linear** *: ( vec3 )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **sRGB To Linear**
- **Inputs**  
	- **Srgb** *: ( vec3 )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **RGB To HSV**
- **Inputs**  
	- **Rgb** *: ( vec3 )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **HSV To RGB**
- **Inputs**  
	- **Hsv** *: ( vec3 | HSV )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **HSV Edit**
- **Inputs**  
	- **Color** *: ( vec4 )*  
	- **Hue** *: ( float )*  
	- **Saturation** *: ( float )*  
	- **Value** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **Bright/Contrast**
- **Inputs**  
	- **Color** *: ( vec4 )*  
	- **Brightness** *: ( float )*  
	- **Contrast** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **Gamma**
- **Inputs**  
	- **Color** *: ( vec4 )*  
	- **Gamma** *: ( float ) - default = 1.0*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **Invert**
- **Inputs**  
	- **Color** *: ( vec4 )*  
	- **Fac** *: ( float | Slider )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **Color Gradient**
---
#### **Gradient**
- **Inputs**  
	- **Color Ramp** *: ( sampler1D )*  
	- **U** *: ( float | Slider )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **RGB Gradient**
- **Inputs**  
	- **Color Ramp** *: ( sampler1D )*  
	- **UVW** *: ( vec3 | Slider )*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **RGBA Gradient**
- **Inputs**  
	- **Color Ramp** *: ( sampler1D )*  
	- **UVWX** *: ( vec4 | Slider )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **Layer Blend**
---
#### **Normal**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Add**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Multiply**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Overlay**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Screen**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Darken**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Lighten**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Soft Light**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Hard Light**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Linear Light**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Dodge**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Burn**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Subtract**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Difference**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Divide**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Hue**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Saturation**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Value**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Color**
- **Inputs**  
	- **Opacity** *: ( float | Slider ) - default = 1.0*  
	- **Base** *: ( vec4 )*  
	- **Blend** *: ( vec4 ) - default = (0.0, 0.0, 0.0, 0.0)*  
	- **Mode** *: ( int | ENUM(Linear,Linear Clamp,sRGB,sRGB Clamp) )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
## Texturing
---
### **Image**
- **Inputs**  
	- **Image** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **Smooth Interpolation** *: ( bool ) - default = True*  
- **Outputs**  
	- **Color** *: ( vec4 )*  
	- **Resolution** *: ( vec2 )*  
---
### **Normal Map**
- **Inputs**  
	- **Texture** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **UV Index** *: ( int )*  
- **Outputs**  
	- **Normal** *: ( vec3 )*  
---
### **Flipbook**
- **Inputs**  
	- **Texture** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **Dimensions** *: ( ivec2 )*  
	- **Page** *: ( float )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **Flowmap**
- **Inputs**  
	- **Texture** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **Flow** *: ( vec2 ) - default = vec2(0.0)*  
	- **Progression** *: ( float )*  
	- **Samples** *: ( int ) - default = 2*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **Matcap**
- **Inputs**  
	- **Matcap** *: ( sampler2D )*  
	- **Normal** *: ( vec3 | Normal ) - default = NORMAL*  
- **Outputs**  
	- **Color** *: ( vec4 )*  
	- **Uv** *: ( vec2 )*  
---
### **HDRI**
- **Inputs**  
	- **Hdri** *: ( sampler2D )*  
	- **Normal** *: ( vec3 | Normal ) - default = NORMAL*  
- **Outputs**  
	- **Color** *: ( vec4 )*  
	- **Uv** *: ( vec2 )*  
---
### **Noise**
---
#### **Infinite**
- **Inputs**  
	- **Coord** *: ( vec3 | Vector ) - default = POSITION*  
	- **Seed** *: ( float )*  
	- **Scale** *: ( float ) - default = 5.0*  
	- **Detail** *: ( float ) - default = 3.0*  
	- **Balance** *: ( float | Slider ) - default = 0.5*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Tiled**
- **Inputs**  
	- **Coord** *: ( vec3 | Vector ) - default = POSITION*  
	- **Seed** *: ( float )*  
	- **Scale** *: ( float ) - default = 5.0*  
	- **Detail** *: ( float ) - default = 3.0*  
	- **Balance** *: ( float | Slider ) - default = 0.5*  
	- **Tile Size** *: ( ivec4 | Vector ) - default = (5, 5, 5, 5)*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **Voronoi**
---
#### **Infinite**
- **Inputs**  
	- **Coord** *: ( vec3 | Vector ) - default = POSITION*  
	- **Seed** *: ( float )*  
	- **Scale** *: ( float ) - default = 5.0*  
- **Outputs**  
	- **Cell Color** *: ( vec4 )*  
	- **Cell Position** *: ( vec4 )*  
	- **Cell Distance** *: ( float )*  
---
#### **Tiled**
- **Inputs**  
	- **Coord** *: ( vec3 | Vector ) - default = POSITION*  
	- **Seed** *: ( float )*  
	- **Scale** *: ( float ) - default = 5.0*  
	- **Tile Size** *: ( ivec4 | Vector ) - default = (5, 5, 5, 5)*  
- **Outputs**  
	- **Cell Color** *: ( vec4 )*  
	- **Cell Position** *: ( vec4 )*  
	- **Cell Distance** *: ( float )*  
---
### **Bayer Pattern**
- **Inputs**  
	- **Size** *: ( int | ENUM(2x2,3x3,4x4,8x8) ) - default = 2*  
	- **Texel** *: ( vec2 ) - default = vec2(screen_pixel())*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **Gradient**
---
#### **Linear**
- **Inputs**  
	- **Value** *: ( float ) - default = UV[0].x*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Quadratic**
- **Inputs**  
	- **Value** *: ( float ) - default = UV[0].x*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Easing**
- **Inputs**  
	- **Value** *: ( float ) - default = UV[0].x*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Diagonal**
- **Inputs**  
	- **UV** *: ( vec2 ) - default = UV[0]*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Spherical**
- **Inputs**  
	- **Vector** *: ( vec3 | Vector ) - default = POSITION*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Quadratic Sphere**
- **Inputs**  
	- **Vector** *: ( vec3 | Vector ) - default = POSITION*  
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Radial**
- **Inputs**  
	- **UV** *: ( vec2 ) - default = UV[0]*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **Wave**
- **Inputs**  
	- **Mode** *: ( int | ENUM(Sine,Saw,Triangle) )*  
	- **Coord** *: ( float ) - default = UV[0].x*  
	- **Scale** *: ( float ) - default = 5.0*  
	- **Phase** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
## Shading
---
### **Ambient Occlusion**
- **Inputs**  
	- **Samples** *: ( int ) - default = 32*  
	- **Radius** *: ( float ) - default = 1.0*  
	- **Distribution Exponent** *: ( float ) - default = 5.0*  
	- **Contrast** *: ( float | Slider ) - default = 0.1*  
	- **Bias** *: ( float | Slider ) - default = 0.01*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **Curvature**
---
#### **Curvature**
- **Outputs**  
	- **result** *: ( float )*  
---
#### **Surface Curvature**
- **Inputs**  
	- **Depth Range** *: ( float ) - default = 0.1*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **Line Detection**
- **Outputs**  
	- **Delta Distance** *: ( float )*  
	- **Delta Angle** *: ( float )*  
	- **Is ID Boundary** *: ( vec4 )*  
---
### **Line Width**
- **Inputs**  
	- **Width Scale** *: ( float ) - default = 4.0*  
	- **Width Units** *: ( int | ENUM(Pixel,Screen,World) )*  
	- **Depth Width** *: ( float | Slider ) - default = 1.0*  
	- **Depth Threshold** *: ( float | Slider ) - default = 0.1*  
	- **Depth Threshold Range** *: ( float | Slider )*  
	- **Normal Width** *: ( float | Slider ) - default = 1.0*  
	- **Normal Threshold** *: ( float | Slider ) - default = 0.5*  
	- **Normal Threshold Range** *: ( float | Slider )*  
	- **Id Boundary Width** *: ( vec4 | Slider ) - default = (1.0, 1.0, 1.0, 1.0)*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **Rim Light**
- **Inputs**  
	- **Normal** *: ( vec3 | Normal ) - default = NORMAL*  
	- **Angle** *: ( float )*  
	- **Rim Length** *: ( float ) - default = 2.0*  
	- **Length Falloff** *: ( float )*  
	- **Thickness** *: ( float ) - default = 0.1*  
	- **Thickness Falloff** *: ( float )*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **NPR Diffuse**
---
#### **Color Ramp**
- **Inputs**  
	- **Base Color** *: ( vec3 ) - default = (0.0, 0.0, 0.0)*  
	- **Color** *: ( vec3 ) - default = (1.0, 1.0, 1.0)*  
	- **Gradient** *: ( sampler1D )*  
	- **Offset** *: ( float | Slider )*  
	- **Full Range** *: ( bool )*  
	- **Max Contribution** *: ( bool )*  
	- **Shadows** *: ( int | ENUM(Enable Shadows,Disable Self-Shadows,Disable Shadows) )*  
	- **Light Groups** *: ( ivec4 ) - default = (1, 0, 0, 0)*  
	- **Position** *: ( vec3 | Vector ) - default = POSITION*  
	- **Normal** *: ( vec3 | Normal ) - default = NORMAL*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Color Layer**
- **Inputs**  
	- **Base Color** *: ( vec3 ) - default = (0.0, 0.0, 0.0)*  
	- **Color** *: ( vec3 ) - default = (1.0, 1.0, 1.0)*  
	- **Size** *: ( float | Slider ) - default = 1.0*  
	- **Gradient Size** *: ( float | Slider ) - default = 0.1*  
	- **Offset** *: ( float | Slider )*  
	- **Full Range** *: ( bool )*  
	- **Max Contribution** *: ( bool )*  
	- **Shadows** *: ( int | ENUM(Enable Shadows,Disable Self-Shadows,Disable Shadows) )*  
	- **Light Groups** *: ( ivec4 ) - default = (1, 0, 0, 0)*  
	- **Position** *: ( vec3 | Vector ) - default = POSITION*  
	- **Normal** *: ( vec3 | Normal ) - default = NORMAL*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
### **NPR Specular**
---
#### **Color Ramp**
- **Inputs**  
	- **Base Color** *: ( vec3 ) - default = (0.0, 0.0, 0.0)*  
	- **Color** *: ( vec3 ) - default = (1.0, 1.0, 1.0)*  
	- **Gradient** *: ( sampler1D )*  
	- **Offset** *: ( float | Slider )*  
	- **Roughness** *: ( float | Slider ) - default = 0.5*  
	- **Anisotropy** *: ( float | Slider ) - default = 0.5*  
	- **Max Contribution** *: ( bool )*  
	- **Shadows** *: ( int | ENUM(Enable Shadows,Disable Self-Shadows,Disable Shadows) )*  
	- **Light Groups** *: ( ivec4 ) - default = (1, 0, 0, 0)*  
	- **Position** *: ( vec3 | Vector ) - default = POSITION*  
	- **Normal** *: ( vec3 | Normal ) - default = NORMAL*  
	- **Tangent** *: ( vec3 | Normal ) - default = radial_tangent(NORMAL, vec3(0,0,1))*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
#### **Color Layer**
- **Inputs**  
	- **Base Color** *: ( vec3 ) - default = (0.0, 0.0, 0.0)*  
	- **Color** *: ( vec3 ) - default = (1.0, 1.0, 1.0)*  
	- **Size** *: ( float | Slider ) - default = 1.0*  
	- **Gradient Size** *: ( float | Slider ) - default = 0.1*  
	- **Offset** *: ( float | Slider )*  
	- **Roughness** *: ( float | Slider ) - default = 0.5*  
	- **Anisotropy** *: ( float | Slider ) - default = 0.5*  
	- **Max Contribution** *: ( bool )*  
	- **Shadows** *: ( int | ENUM(Enable Shadows,Disable Self-Shadows,Disable Shadows) )*  
	- **Light Groups** *: ( ivec4 ) - default = (1, 0, 0, 0)*  
	- **Position** *: ( vec3 | Vector ) - default = POSITION*  
	- **Normal** *: ( vec3 | Normal ) - default = NORMAL*  
	- **Tangent** *: ( vec3 | Normal ) - default = radial_tangent(NORMAL, vec3(0,0,1))*  
- **Outputs**  
	- **result** *: ( vec3 )*  
---
## Filter
---
### **Curvature**
- **Inputs**  
	- **Normal Texture** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **Width** *: ( float ) - default = 1.0*  
	- **X** *: ( vec3 | Normal ) - default = (1.0, 0.0, 0.0)*  
	- **Y** *: ( vec3 | Normal ) - default = (0.0, 1.0, 0.0)*  
- **Outputs**  
	- **result** *: ( float )*  
---
### **Blur**
---
#### **Box Blur**
- **Inputs**  
	- **Texture** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **Radius** *: ( float ) - default = 5.0*  
	- **Circular** *: ( bool )*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Gaussian Blur**
- **Inputs**  
	- **Texture** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **Radius** *: ( float ) - default = 5.0*  
	- **Sigma** *: ( float ) - default = 1.0*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Jitter Blur**
- **Inputs**  
	- **Texture** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **Radius** *: ( float ) - default = 5.0*  
	- **Distribution Exponent** *: ( float ) - default = 5.0*  
	- **Samples** *: ( int ) - default = 8*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Bilateral**
- **Inputs**  
	- **Input Texture** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **Radius** *: ( float ) - default = 5*  
	- **Sigma** *: ( float ) - default = 10.0*  
	- **BSigma** *: ( float ) - default = 0.1*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Orientation-Aligned Bilateral**
- **Inputs**  
	- **Input Texture** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **Flow** *: ( vec2 ) - default = vec2(0)*  
	- **Radius** *: ( float ) - default = 6.0*  
	- **Smoothness** *: ( float ) - default = 0.55*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **Sharpen**
---
#### **Box**
- **Inputs**  
	- **Texture** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **Radius** *: ( float ) - default = 1.0*  
	- **Circular** *: ( bool )*  
	- **Sharpness** *: ( float ) - default = 0.3*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Gaussian**
- **Inputs**  
	- **Texture** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **Radius** *: ( float ) - default = 1.0*  
	- **Sigma** *: ( float ) - default = 1.0*  
	- **Sharpness** *: ( float ) - default = 0.3*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Jitter**
- **Inputs**  
	- **Texture** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **Radius** *: ( float ) - default = 1.0*  
	- **Distribution Exponent** *: ( float ) - default = 5.0*  
	- **Samples** *: ( int ) - default = 8*  
	- **Sharpness** *: ( float ) - default = 0.3*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
### **Kuwahara**
---
#### **Isotropic**
- **Inputs**  
	- **Texture** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **Size** *: ( int ) - default = 5*  
- **Outputs**  
	- **result** *: ( vec4 )*  
---
#### **Anisotropic**
- **Inputs**  
	- **Texture** *: ( sampler2D )*  
	- **UV** *: ( vec2 ) - default = UV[0]*  
	- **Direction** *: ( vec2 ) - default = vec2(0.0, 0.0)*  
	- **Size** *: ( float ) - default = 2.0*  
	- **Samples** *: ( int ) - default = 50*  
- **Outputs**  
	- **result** *: ( vec4 )*  
