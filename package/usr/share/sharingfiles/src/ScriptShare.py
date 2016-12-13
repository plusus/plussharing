class ScriptShare:
    def __init__(self, inPathsArgument, inNamesArgument):
        """
        Will load the files' paths and names into the class
        :param inPathsArgument: the script arguments representing the files' paths separated by spaces
        :param inNamesArgument:the script arguments representing the files' names separated by spaces
        """
        self.pathsArgument = inPathsArgument
        self.namesArgument = inNamesArgument
        self.pathsList = []
        self.namesList = []
        self.pathsList = self.get_files_list('Paths')
        self.namesList = self.get_files_list('Names')


    def get_files_list(self, inListType):
        """
        Split the arguments received in the __init__ method of the class into a list of string
        :param inListType: Has to be either 'Paths' or 'Names' cause it specifies which list to return.
        :return: the list paths of names depending on the inListType
        """
        if inListType == 'Paths':
            if(len(self.pathsList) < 1) :
                self.pathsList = str(self.pathsArgument).split(' ')
                if self.pathsList[len(self.pathsList) - 1] == '':
                    self.pathsList.remove(self.pathsList[len(self.pathsList) - 1])

            return self.pathsList
        elif inListType == 'Names':
            if (len(self.namesList) < 1):
                self.namesList = str(self.namesArgument).split(' ')
                if self.namesList[len(self.namesList) - 1] == '':
                    self.namesList.remove(self.namesList[len(self.namesList) - 1])

            return self.namesList


    def get_files_paths_from_names(self, inNames):
        """
        Find the filepaths specified for the filenames received
        :param inNames: The list of filenames
        :return: the list of filepaths linked to the filenames received
        """
        pathsListToShare = []

        nameIndex = 0
        for name in inNames:
            if (name == self.namesList[nameIndex]):
                pathsListToShare.append(self.pathsList[nameIndex])

            nameIndex = nameIndex + 1

        return pathsListToShare