# ImageWAO
An image processing and data management tool for the Namibia Wildlife Aerial Observatory (WAO) research program.

## Build Instructions
Create new environment with python 3.6, then install the following packages.
```
pip install fbs pyside2 pillow
fbs run
```

## Screenshot
![Screenshot of two Oryx](/assets/images/twoMarkedAnimals.png)

## TODO
* Improve zooming features: (inspiration from BOTW Object Map)
* Save import log/meta data in text file. Include path mapping -- DSC_0101.jpg -> Transect01.jpg
* Create UI form to edit/view flight metadata
* Visual separation of different images in grid viewer (new delegate?)
* Better line width image
* Create UI/logic for Count Totals form
