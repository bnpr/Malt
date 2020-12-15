# Render Library

Any *Pipeline* agnostic render utility that can't be implemented only as *GLSL* code should go here.  
From simple *Uniform Buffer Objects* ([Common.py](Common.py)) and pure *Python* utilities ([Sampling.py](Sampling.py)) to more complex features like Lighting and Shadowmaps ([Lighting.py](Lighting.py)).

*Render* modules don't follow any specific API and while similar features share a similar interface, they are free to implement the most appropriate for their needs.

As more features are implemented and common patterns arise, a *Pipeline Plugins* API can be designed so using this utilities requires less manual communication from the *Pipeline* side.

