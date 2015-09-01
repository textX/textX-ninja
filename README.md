# **TextX ninja**

Ninja IDE plugin for textX, support for visualisation and syntax coloring.

## **Dependencies**

- [Ninja IDE] (https://github.com/ninja-ide/ninja-ide)
- [TextX] (https://github.com/igordejanovic/textX)
- [pydot] (https://github.com/erocarrera/pydot)

## **User guide**

After all dependencies are in place and project is imported in Ninja IDE, 
plugin can be tested from Plugin Tools option of Ninja IDE.

TextX project can be created from new project wizard choosing the option 'textX Project':<br />
![alt tag](https://raw.githubusercontent.com/masatalovic/textX-ninja/master/art/new_project.png)

File with name 'metamodel.tx' is created with new project so that user can immediately start testing the plugin.<br />
Syntax coloring for metamodel:<br />
![alt tag](https://raw.githubusercontent.com/masatalovic/textX-ninja/master/art/metamodel.png)

After every change (key pressed, file in focus changed, file saved, file opened) visualisation of metamodel/model is exported to svg file 
if metamodel/model is in correct state and visualisation of metamodel/model is showed 
in last tab of misc part of Ninja IDE GUI.<br />
![alt tag](https://raw.githubusercontent.com/masatalovic/textX-ninja/master/art/metamodel_svg.png)

There can be multiple models in one project, but only one at the time is going to be visualized
(last one changed, last one in focus or last one saved).<br />
![alt tag](https://raw.githubusercontent.com/masatalovic/textX-ninja/master/art/model_svg.png)


## **Authors**

- [Maša Talović] (https://github.com/masatalovic/)

This tool is being developed by master students under the menthorship of [Igor Dejanović] (https://github.com/igordejanovic)
