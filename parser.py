__author__ = 'fenixlin'

class Parser(object):
    #parse raw data into sortable rating data with attribute matrix

    def __init__(self, ratingfile, itemfile, userfile):
        self.ratingfile = ratingfile
        self.itemfile = itemfile
        self.userfile = userfile

        self.rating_data = None
        self.item_info = None
        self.user_info = None

    def extract_rating_list(self, sort_data):
        raise Exception("unimplemented abstract method")

    def extract_attr_list(self):
        raise Exception("unimplemented abstract method")

    def parse_line(self, rating_record):
        #parse IDs starting from 0
        raise Exception("unimplemented abstract method")

    def _get_user_info(self):
        #parse item informations for rating sorting
        raise Exception("unimplemented abstract method")

    def _get_item_info(self):
        #parse item informations for rating sorting
        raise Exception("unimplemented abstract method")

    def load_raw_data(self, sep='\t'):
        #separator in raw data lines is '\t' in default
        file_ratingfile = open(self.ratingfile)
        rating_data_list = file_ratingfile.readlines()
        self.rating_data = [x.split(sep) for x in rating_data_list]
        file_ratingfile.close()
        self.RATING_NUM = len(self.rating_data)

        if self.itemfile != None:
            file_itemfile = open(self.itemfile)
            item_info_list = file_itemfile.readlines()
            self.item_info = [x.split(sep) for x in item_info_list]
            file_itemfile.close()
            self.ITEM_NUM = len(self.item_info)
        else:
            self.item_info = None

        if self.userfile != None:
            file_userfile= open(self.userfile)
            user_info_list = file_userfile.readlines()
            self.user_info = [x.split(sep) for x in user_info_list]
            file_userfile.close()
            self.USER_NUM = len(self.user_info)
        else:
            self.user_info = None

    def get_item_num(self):
        return self.ITEM_NUM

    def get_user_num(self):
        return self.USER_NUM

    def get_item_num_id_dict(self):
        #XXX: I dont get it
        if locals().has_key("item_num_id_dict"):
            return self.item_num_id_dict
        else:
            self.item_num_id_dict = dict()
            for i in range(self.item_num_id_dict):
                self.item_num_id_dict[self.item_num_id_dict[i][0]] = i
            return self.item_num_id_dict
    
    def _sort_rating_list(self, rating_list, keyTuple):
        #keyTuple is a list which contains the keywords in sorting.
        def f(x):
            keyList = []
            for number in keyTuple:
                keyList.append(x[number])
            return tuple(keyList)
        
        return sorted(rating_list, key=lambda x: f(x))

class MLParser(Parser):

    def extract_attr_list(self):
        if self.item_info == None:
            return None
        genre_dict = dict()
        director_dict = dict()
        editor_dict = dict()
        writer_dict = dict()
        cast_dict = dict()
        country_dict = dict()
        language_dict = dict()
        for info in self.item_info:
            self._add_to_dict(info[3], genre_dict)
            self._add_to_dict(info[4], director_dict)
            self._add_to_dict(info[5], editor_dict)
            self._add_to_dict(info[6], writer_dict)
            self._add_to_dict(info[7], cast_dict)
            self._add_to_dict(info[9], country_dict)
            self._add_to_dict(info[10], language_dict)

        bias = [0, len(genre_dict), len(director_dict), len(editor_dict), len(writer_dict), len(cast_dict), len(country_dict)]
        for i in range(len(bias)-1):
            bias[i+1] += bias[i]
        attribute_list = []
        for info in self.item_info:
            tmp = []
            tmp.extend(self._get_attr_from_dict(info[3], genre_dict, bias[0]))
            tmp.extend(self._get_attr_from_dict(info[4], director_dict, bias[1]))
            tmp.extend(self._get_attr_from_dict(info[5], editor_dict, bias[2]))
            tmp.extend(self._get_attr_from_dict(info[6], writer_dict, bias[3]))
            tmp.extend(self._get_attr_from_dict(info[7], cast_dict, bias[4]))
            tmp.extend(self._get_attr_from_dict(info[9], country_dict, bias[5]))
            tmp.extend(self._get_attr_from_dict(info[10], language_dict, bias[6]))
            attribute_list.append(tmp)
        return attribute_list

    def extract_rating_list(self, sort_data):
        rating_list = []
        self.item_num_of_id = dict()
        for record in self.rating_data:
            rating_list.append(self._parse_line(record))
        if sort_data:
            rating_list = self._sort_rating_list(rating_list, [4, 1, 0]) #XXX: better place to specify?
        return rating_list

    def _get_item_info(self, itemID):
        itemProductionDate = self.item_info[itemID][2]
        return [itemProductionDate]

    def _get_user_info(self, userID):
        return []

    def _parse_line(self, values):
        userID = int(values[0])-1
        if self.item_num_of_id.has_key(values[1]):
            itemID = self.item_num_of_id[values[1]]
        else:
            itemID = len(self.item_num_of_id)
            self.item_num_of_id[values[1]] = len(self.item_num_of_id)
        rating = float(values[2])
        commentDate = values[3]
        result = [userID, itemID, rating, commentDate]
        if self.item_info!=None:
            result.extend(self._get_item_info(itemID)) #XXX: item_info is query by num actually
        if self.user_info!=None:
            result.extend(self._get_user_info(userID))
        return result

    def _add_to_dict(self, info, des_dict):
        info = info.split('|')
        for x in info:
            if not des_dict.has_key(x):
                des_dict[x] = len(des_dict)

    def _get_attr_from_dict(self, info, des_dict, bias=0):
        result = []
        info = info.split('|')
        for x in info:
            result.append(des_dict[x]+bias)
        return result

class ML100kParser(Parser):
    """ Every rating record contains: 0:userID 1:itemID 2:rating 3:commentDate 4:itemName 5:itemProductionDate
    6:itemAttribute 7:userAge 8:userGender 9:userOccupation 10:userZipCode
    """

    def _get_item_info(self, itemID):
        if itemID == 267:
            attribute = self.item_attribute_list[itemID-1]
            return "unknown", 22222222, "unknown", attribute
        itemID -= 1
        itemName = self.item_info[itemID][1]
        itemProductionDate = self.item_info[itemID][2]
        itemProductionDate = self._convert_date_to_int(itemProductionDate)
        itemWebsite = self.item_info[itemID][3]
        attribute = self.item_attribute_list[itemID]
        return itemName, itemProductionDate, itemWebsite, attribute

    def _get_user_info(self, userID):
        userID -= 1
        userAge = int(self.user_info[userID][1])
        userGender = self.user_info[userID][2]
        userOccupation = self.user_info[userID][3]
        userZipCode = self.user_info[userID][4].strip()
        return userAge, userGender, userOccupation, userZipCode

    def parse_line(self, rating_record):
        values = rating_record.split()
        userID = values[0]
        itemID = values[1]
        rating = float(values[2])
        commentDate = values[3]
        itemName, itemProductionDate, itemWebsite, itemAttribute = self._get_item_info(itemID)
        userAge, userGender, userOccupation, userZipCode = self._get_user_info(userID)
        one_record = [userID, itemID, rating, commentDate, itemName, itemProductionDate, itemAttribute, userAge, userGender, userOccupation, userZipCode]
        return one_record

    def extract_attr_list(self):
        pass

class AmazonParser(Parser):
    
    def _get_item_info(self, itemID):
        #TODO:       
        #if self.item_info!=None:
        pass

    def _get_user_info(self, userID):
        return []

    def parse_line(self, rating_record):
        userID = rating_record[0]
        itemID = rating_record[1]
        rating = float(rating_record[2])
        commentDate = rating_record[3]
        result = [userID, itemID, rating, commentDate]
        result.extend(_get_item_info(userID))
        result.extend(_get_user_info(itemID))
        return result

    def extract_attr_list(self):
        pass
