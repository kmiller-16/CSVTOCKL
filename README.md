## **Setup Instructions**

Running the `setup.py` will execute the code that will add what you need to the settings and create the directories that the script needs to execute.

Next, move the ckls you're working with into the `data/ckl` directory that was created by the script. *Note that the ckl directory will be located relative to whatever place in your file structure in which you placed the files.*

Finally, run the `populate.py` script. This will create a hash table csv that will enable matches between the spreadsheet csv and the files in the ckl directory.

You can then use csvtockl.py to update your ckls at any time. make sure to enter the full path of your csv as the second command `csvtockl.py [path to csv]`

Note that only certain fields will update as these are the only ones we used. Also there are certain fields that are required in the csv for the script to function. The less messing around you do with the original csv fields generated from STIG Viewer, the better off you will be.

**Background**

This software exists because our team was dropped into a situation where we needed to evaluate an environment and prep an ATO package for an environment that we had little to no involvement with up to that point. Our ISSE ended up working from a massive spreadsheet because none of us knew which systems were derived from a given baseline or not, and I'm not even sure the cloud engineers knew either. 

When it came time to load the updated information into eMASS, we had to be able to convert the data back from csv to ckl in order to progress. I couldn't find a suitable solution to go with our shoe-string budget and infrastructure restrictions. Therefore, I coded my way out of it. FWIW, this is my first project coded in Python. I don't claim to be some kind of programming guru. I did my best with the limited time I had. Feel free to improve/fork if you need to.


> Written with [StackEdit](https://stackedit.io/).