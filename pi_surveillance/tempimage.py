import uuid
import os
 
class TempImage:
    def __init__(self, basePath="images", ext=".jpg"):

        # construct the file path
        
        self.key = "{rand}{ext}".format(rand=str(uuid.uuid4()), ext=ext)
        self.path = "{base_path}/{key}".format(base_path=basePath,key=self.key)    
 
    def cleanup(self):
		# remove the file
        os.remove(self.path)