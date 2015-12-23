__author__ = 'fenixlin'
import os
import cPickle
import random
import numpy

class Parser(object):
    
    @abstractmethod
    def parse_line(self, rating_record):
        pass

    def load_raw_data(self):
        file_ratingfile = open(self.ratingfile)
        rating_data_list = file_ratingfile.readlines()
        self.rating_data = [x.split('\t') for x in rating_data_list]
        file_u_dot_data.close()
        self.RATING_NUM = len(self.rating_data)

        if self.itemfile != None:
            file_itemfile = open(self.itemfile)
            item_info_list = file_itemfile.readlines()
            self.item_info = [x.split('\t') for x in item_info]
            file_itemfile.close()
            self.ITEM_NUM = len(self.item_info)
        else:
            self.item_info = None

        if self.userfile != None:
            file_userfile= open(self.userfile)
            user_info = file_userfile.readlines()
            self.user_info = [x.split('\t') for x in user_info]
            file_userfile.close()
            self.USER_NUM = len(self.user_info)
        else:
            self.user_info = None

    def get_item_num(self):
        return self.ITEM_NUM

    def get_user_num(self):
        return self.USER_NUM

    def get_item_num_id_dict(self):
        if locals().has_key("item_num_id_dict"):
            return self.item_num_id_dict
        else:
            self.item_num_id_dict = dict()
            for i in range(self.item_num_id_dict):
                self.item_num_id_dict[self.item_num_id_dict[i][0]] = i
            return self.item_num_id_dict
    
    def __init__(self):
        item_id_num_dict = dict()
            for record in self.item_info:

    @staticmethod
    def _convert_date_to_int(productionDate):
        """ convert 01-Jan-1995 to 19950101 """
        values = productionDate.split('-')
        dictionary = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                      'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
        values[1] = dictionary[values[1]]
        if len(values[0]) == 1:
            values[0] = '0'+values[0]
        return int(values[2]+values[1]+values[0])

class MLParser(Parser):
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
        #parse IDs starting from 0
        userID = values[0]
        itemID = values[1]
        rating = float(values[2])
        commentDate = values[3]
        itemName, itemProductionDate, itemWebsite, itemAttribute = self._get_item_info(itemID)
        userAge, userGender, userOccupation, userZipCode = self._get_user_info(userID)
        one_record = [userID, itemID, rating, commentDate, itemName, itemProductionDate, itemAttribute, userAge, userGender, userOccupation, userZipCode]
        return one_record

class AmazonParser(Parser):
    
    def _get_item_info(self, itemID):
        if self.item_info!=None:
        #TODO:       

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

class Database(object):

    def __init__(self, dataFormat, user_num, item_num, ratingfile, itemfile=None, userfile=None):
        if dataFormat=="movielens":
            self.parser = MLParser()
        elif dataFormat=="amazon":
            self.parser = AmazonParser()
        else
            raise ValueError
            
        # nums must be explicitly assigned, since we won't get it from recovered data directly 
        self.USER_NUM = user_num
        self.ITEM_NUM = item_num
        
        self.itemfile = itemfile
        self.ratingfile = ratingfile
        self.userfile = userfile

        self.out_rating_data = []

        """ this is the prime data, slice and sort are all executed on this data list"""
        self.core_data = []
        self.libfm_data = []

        """ this is the alternative data, used in step 1 binary classification """
        self.alternative_user_item_matrix = dict()
        self.alternative_item_user_matrix = dict()
        self.alternative_user_set = set()
        self.alternative_item_set = set()
        self.rating_matrix = []

    def make_data(self, sort_order=None):
        self.datadir = "./Generate"
        if self._recover_dumpable_data("dumpable.data")==False:
            self._load_raw_data()
            self._generate_and_dump_data(parser)
            self._dump_core_data("dumpable.data")
        if sort_order!=None:
            self._sort_data(sort_order)
        self._extract_rating_matrix()
        #TODO:
        self._make_trainning_data()
        self._make_test_data()

    def _load_raw_data():
        self.parser.load_raw_data()

    def _recover_dumpable_data(self, filename):
        if os.path.exists(filename):
            f = open(filename, mode='rb')
            self.core_data = cPickle.load(f)
            f.close()
            return True
        else:
            return False

    def _generate_dumpable_data(self, parser):
        for record in self.rating_data:
            self.core_data.append(self.parser.parse_line(record))

    def _dump_core_data(self, filename):
        if not os.path.exists(self.datadir):
            os.makedirs(self.datadir)
        f = open(self.datadir+filename, 'wb')
        cPickle.dump(self.core_data, f, protocol=2)
        f.close()

    def _sort_data(self, keyTuple, data_list=None):
        #XXX:data_list??
        #keyTuple is a list which contains the keywords in sorting.
        if data_list is None:
            data_list = self.core_data
        def f(x):
            keyList = []
            for number in keyTuple:
                keyList.append(x[number])
            return tuple(keyList)
        self.core_data = sorted(data_list, key=lambda x: f(x))

    def add_negative_data(self, data_list=None, addAllUsers=False):
        #XXX:
        """if this is test data for binary classification, then you should choose addAllUsers """
        if data_list is None:
            data_list = self.core_rating_data

        self.out_rating_data = data_list[:]
        self.make_user_item_rating_matrix(data_list)

        negative_data = []
        if addAllUsers:
            for itemID in self.itemID_set:
                for userID in range(1, self.TOTAL_USERS+1):
                    if self.item_user_rating_matrix[itemID].get(userID) is None:
                        negative_data.append([userID, itemID, -1])
        else:
            while len(negative_data) < len(data_list):
                userID = random.choice(list(self.userID_set))
                itemID = random.choice(list(self.itemID_set))
                if self.user_item_rating_matrix[userID].get(itemID) is None:
                    negative_data.append([userID, itemID, -1])

        self.out_rating_data.extend(negative_data)

    def _generate_libfm_data(self, filename, shuffle=True, omit_item=False):
        #XXX:
        # output libfm format data from core data
        # [rating item attribute] if omit_item==False, [rating attribute] if omit_item==True

        libfm_data = []
        for values in self.core_data:
            userID = values[0]
            itemID = values[1]
            rating = values[2]
            libfm_line = [rating, str(userID)+':1']
            filled_num = self.USER_NUM

            if not omit_item:
                libfm_line.append(str(itemID+filled_num) + ':1')
                filled_num += self.ITEM_NUM

            #TODO: check if attribute are correctly parsed (wtf, attr_list directly from file?)
            for attribute_pos in range(len(self.item_attribute_list[itemID])):
                if self.item_attribute_list[itemID][attribute_pos] == '1':
                    libfm_line.append(str(count+attribute_pos) + ':1')
            libfm_data.append(libfm_line)

        if shuffle:
            random.shuffle(libfm_data)

        #TODO: output libfm data

    def _extract_rating_matrix(self):
        # get rating matrix from sorted rating data(one rating per line)
        row_num_of_item_id = [-1 for i in range(self.ITEM_NUM)]
        rating_matrix = numpy.zeros([self.USER_NUM, self.ITEM_NUM])
        item_count = 0
        for values in self.core_data:
            userID = values[0]
            itemID = values[1]
            if row_num_of_item_id[itemID] == 0:
                item_count += 1
                row_num_of_item_id[itemID] = item_count
            rating = values[2]
            rating_matrix[userID, row_num_of_item_id[itemID]] = rating
        rating_matrix = rating_matrix[:, :item_count]
        print 'rating matrix is {0}*{1}'.format(self.USER_NUM, item_count)
        self.rating_matrix = rating_matrix

##########################################################################
    #XXX:not that necessary
    def store_data_to_file(self, data_list=None, fileName='a.out', serialization=False, slice_range=None):
        #XXX:dumping core data
        """ slice_range is only a slice of record's position in this data_list """
        if data_list is None:
            data_list = self.core_rating_data
        if slice_range:
            slice_range = set(slice_range)

        f = open('./Generate/'+fileName, mode='w+' if not serialization else 'wb+')
        data_list_dumped = []
        for data_pos in range(len(data_list)):
            if slice_range and data_pos not in slice_range:
                continue
            one_data = data_list[data_pos]
            if serialization:
                data_list_dumped.append(one_data)
            else:
                for i in range(len(one_data)):
                    f.write(str(one_data[i]))
                    if i != len(one_data)-1:
                        f.write(' ')
                f.write('\n')
        if serialization:
            cPickle.dump(data_list_dumped, f, protocol=2)
        f.close()

    def make_shuffle(self):
        #XXX:we use it nowhere
        self.out_rating_data = self.core_rating_data[:]
        random.shuffle(self.out_rating_data)

    def make_alternative_user_item_matrix(self, data_list):
        #XXX:we use it nowhere!
        self.alternative_user_item_matrix.clear()
        self.alternative_item_user_matrix.clear()

        self.alternative_user_set.clear()
        self.alternative_item_set.clear()
        for values in data_list:
            userID = values[0]
            itemID = values[1]
            self.alternative_user_set.add(userID)
            self.alternative_item_set.add(itemID)
            if self.alternative_user_item_matrix.get(userID) is None:
                self.alternative_user_item_matrix[userID] = dict()
                self.alternative_user_item_matrix[userID][itemID] = True
            else:
                self.alternative_user_item_matrix[userID][itemID] = True

            if self.alternative_item_user_matrix.get(itemID) is None:
                self.alternative_item_user_matrix[itemID] = dict()
                self.alternative_item_user_matrix[itemID][userID] = True
            else:
                self.alternative_item_user_matrix[itemID][userID] = True

    def make_slice(self, userID_slice=None, itemID_slice=None, rating_slice=None, data_list=None,
                   itemProductionDate_slice=None, count_item_slice=None):
        #XXX: deprecated - why not just slice outside????
        """ id slice = set([x1,x2,x3, ...])   itemProduction_slice = [start, end]
        count_item_slice reads items and takes counts, it will select the number start to end items
        """
        if data_list is None:
            data_list = self.core_rating_data

        def f(x):
            if x is not None:
                return set(x)
            return None
        userID_slice = f(userID_slice)
        itemID_slice = f(itemID_slice)
        rating_slice = f(rating_slice)
        count_item_slice = f(count_item_slice)

        start_date = end_date = 0
        if itemProductionDate_slice:
            start_date = itemProductionDate_slice[0]
            end_date = itemProductionDate_slice[1]

        already_count_item_set = set()
        self.out_rating_data = []
        for values in data_list:
            already_count_item_set.add(values[1])  # add this item into count_item set
            item_ranking_number = len(already_count_item_set)  # this item's No
            if (userID_slice and values[0] not in userID_slice) or (itemID_slice and values[1] not in itemID_slice) \
                or (rating_slice and values[2] not in rating_slice) \
                    or (count_item_slice and item_ranking_number not in count_item_slice) \
                    or (itemProductionDate_slice and (end_date < values[5] or values[5] < start_date)):
                continue
            self.out_rating_data.append(values)

    def load_core_rating_data(self, data_list):
        #XXX:
        self.core_rating_data = data_list[:]

    def extract_data_from_file(self, fileName):
        #XXX:
        f = open('./Generate/'+fileName, mode='rb')
        self.core_rating_data = cPickle.load(f)
        f.close()

    def _calculate_item_avg_user_mse(self):
        #XXX:cal with numpy
        self.make_user_item_rating_matrix(self.core_data)
        self.item_avg_rating = [0] * (self.TOTAL_NUM+1)
        self.user_MSE = [0] * (self.TOTAL_USERS+1)
        for itemID in self.item_user_rating_matrix:
            rating_sum = 0
            rating_num = 0
            for userID in self.item_user_rating_matrix[itemID]:
                rating_num += 1
                rating_sum += self.item_user_rating_matrix[itemID][userID]
            self.item_avg_rating[itemID] = float(rating_sum)/rating_num
        for userID in self.user_item_rating_matrix:
            for itemID in self.user_item_rating_matrix[userID]:
                difference = (float(self.user_item_rating_matrix[userID][itemID])-self.item_avg_rating[itemID])
                self.user_MSE[userID] += difference*difference

        self.calculate_item_avg_user_mse()

    #XXX
class DataProcess(object):

    def __init__(self):
        self.train_original_data = []
        self.train_addNegative_data = []
        self.test_original_data = []
        self.test_addAllNegative_data = []

        self.train_rating_numpy_matrix = []
        self.train_from_item_id_get_item_num = []
        self.train_from_item_num_get_item_id = []
        self.test_rating_numpy_matrix = []
        self.test_from_item_id_get_item_num = []
        self.test_from_item_num_get_item_id = []
        self.itemDataBase = None
        self.generate_data()

    def generate_data(self):
        db = Database()
        db.load_data_from_file()
        db.generate_dumpable_data(regenerate=False)

        self.TRAIN_NUM = 1200
        self.TEST_NUM = 240

        itemDataBase.make_sorted_rating_data([5, 1, 0])
        sorted_rating_data = itemDataBase.out_rating_data[:]
        itemDataBase.synchronize()
        itemDataBase.make_slice(count_item_slice=range(1, self.TRAIN_NUM+1))
        itemDataBase.synchronize()
        itemDataBase.compute_numpy_matrix()
        self.train_rating_numpy_matrix = itemDataBase.numpy_rating_matrix
        self.train_from_item_num_get_item_id = itemDataBase.from_item_num_get_item_id
        self.train_from_item_id_get_item_num = itemDataBase.from_item_id_get_item_num

        self.train_original_data = itemDataBase.core_rating_data[:]
        itemDataBase.store_data_to_file(fileName='train_original_data')
        itemDataBase.generate_libfm_data(omit=True)
        itemDataBase.store_data_to_file(itemDataBase.libfm_data, 'train_step2.libfm')

        itemDataBase.add_negative_data()
        itemDataBase.synchronize()
        self.train_addNegative_data = itemDataBase.core_rating_data[:]
        itemDataBase.store_data_to_file(fileName='train_addNegative_data')
        itemDataBase.generate_libfm_data(omit=True)
        itemDataBase.store_data_to_file(itemDataBase.libfm_data, 'train_step1.libfm')

        itemDataBase.load_core_rating_data(sorted_rating_data)
        itemDataBase.make_slice(count_item_slice=range(self.TRAIN_NUM+1, self.TRAIN_NUM+self.TEST_NUM+1))
        itemDataBase.synchronize()
        itemDataBase.compute_numpy_matrix()
        self.test_rating_numpy_matrix = itemDataBase.numpy_rating_matrix
        self.test_from_item_num_get_item_id = itemDataBase.from_item_num_get_item_id
        self.test_from_item_id_get_item_num = itemDataBase.from_item_id_get_item_num

        self.test_original_data = itemDataBase.core_rating_data[:]
        itemDataBase.store_data_to_file(fileName='test_original_data')
        itemDataBase.generate_libfm_data(shuffle=False)
        itemDataBase.store_data_to_file(itemDataBase.libfm_data, fileName='test_step3.libfm')

        itemDataBase.add_negative_data(addAllUsers=True)
        itemDataBase.synchronize()
        self.test_addAllNegative_data = itemDataBase.core_rating_data[:]
        itemDataBase.store_data_to_file(fileName='test_addAllNegative_data')
        itemDataBase.generate_libfm_data(omit=True, shuffle=False)
        itemDataBase.store_data_to_file(itemDataBase.libfm_data, 'test_step1.libfm')
        itemDataBase.store_data_to_file(itemDataBase.libfm_data, 'test_step2.libfm')
        self.itemDataBase = itemDataBase
