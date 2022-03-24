# How to Setup BlenderMalt for Development

- Clone the repository.  
`git clone https://github.com/bnpr/Malt.git`
- Set a user scripts folder for Blender if you don't have one.  
[*Blender > Preferences > File Paths > Scripts*](https://docs.blender.org/manual/en/latest/editors/preferences/file_paths.html)
- Locate the *Python* executable from your *Blender* installation or your system's *Python* installation.  
For example: ```"C:\Program Files\Blender Foundation\Blender 2.93\2.93\python\bin\python.exe"```
- Run: ```<Blender Python Path> <Cloned Repo Path>/scripts/setup_blender_addon.py --scripts-folder <User Scripts Path>```

> The setup script will try to compile the CBlenderMalt and the Bridge ipc libraries using CMake,  
> if you don't have the required toolchain you can just copy them from the Github release.

Now if you restart *Blender* and go to *Preferences > Add-ons*, you should be able to enable *BlenderMalt*.
