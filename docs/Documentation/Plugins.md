# Plugins

Render pipelines can be customized through plugins.
Plugins can:
- Add new node libraries to *Pipeline Graphs*.
- Add new *Pipeline Parameters*.
- Add new *PipelineGraph types*.

Plugins can be installed globally in the *Addon Settings* or per world in the *World Panel*.

A basic example can be found in [Development/plugins](https://github.com/bnpr/Malt/tree/Development/plugins)

> The Plugins path should point to the plugins parent folder, then any plugin that you drop into that folder should be automatically loaded.  

> For example, the Plugins path shouldn't point to `C:/Malt-plugins/My-plugin-example/`, it should point to `C:/Malt-plugins/`
