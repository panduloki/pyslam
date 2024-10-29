"""
* This file is part of PYSLAM 
*
* Copyright (C) 2016-present Luigi Freda <luigi dot freda at gmail dot com> 
*
* PYSLAM is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* PYSLAM is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with PYSLAM. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import csv
import json
import numpy as np 
from enum import Enum
from utils_sys import Printer 


class GroundTruthType(Enum):
    NONE = 1
    KITTI = 2
    TUM = 3
    EUROC = 4
    SIMPLE = 5


kScaleSimple = 1 
kScaleKitti = 1   
kScaleTum = 1    
kScaleEuroc = 1  


def groundtruth_factory(settings):

    type=GroundTruthType.NONE
    associations = None 

    type = settings['type']
    path = settings['base_path']
    name = settings['name']
           
    start_frame_id = 0
    if 'start_frame_id' in settings:
        Printer.orange(f'groundtruth_factory - start_frame_id: {settings["start_frame_id"]}')
        start_frame_id = int(settings['start_frame_id'])
                   
    print('using groundtruth: ', type)   
    if type == 'kitti':         
        return KittiGroundTruth(path, name, associations, start_frame_id, GroundTruthType.KITTI)
    if type == 'tum':          
        if 'associations' in settings:
            associations = settings['associations']        
        return TumGroundTruth(path, name, associations, start_frame_id, GroundTruthType.TUM)
    if type == 'euroc':         
        return EurocGroundTruth(path, name, associations, start_frame_id, GroundTruthType.EUROC)
    if type == 'video' or type == 'folder':   
        name = settings['groundtruth_file']
        return SimpleGroundTruth(path, name, associations, start_frame_id, GroundTruthType.SIMPLE)     
    else:
        print('not using groundtruth')
        print('if you are using main_vo.py, your estimated trajectory will not make sense!')          
        return GroundTruth(path, name, associations, start_frame_id, type=GroundTruthType.NONE)


# base class 
class GroundTruth(object):
    def __init__(self, path, name, associations=None, start_frame_id=0, type=GroundTruthType.NONE):
        self.path=path 
        self.name=name 
        self.type=type    
        self.associations=associations 
        self.filename=None
        self.file_associations=None         
        self.data=None 
        self.scale = 1
        self.start_frame_id=start_frame_id
        
        self.trajectory = None 
        self.timestamps = None

    def getDataLine(self, frame_id):
        frame_id+=self.start_frame_id
        return self.data[frame_id].strip().split()
 
    # return timestamp,x,y,z,scale
    def getTimePoseAndAbsoluteScale(self, frame_id):
        frame_id+=self.start_frame_id
        return 1,0,0,0,1

    # convert the dataset into 'Simple' format  [x,y,z,scale]
    def convertToSimpleXYZ(self, filename='groundtruth.txt'):
        out_file = open(filename,"w")
        num_lines = len(self.data)
        for ii in range(num_lines):
            timestamp,x,y,z,scale = self.getTimePoseAndAbsoluteScale(ii)
            if ii == 0:
                scale = 1 # first sample: we do not have a relative 
            out_file.write( "%f %f %f %f %f\n" % (timestamp,x,y,z,scale) )
        out_file.close()

    def getNumSamples(self): 
        num_lines = len(self.data)
        return num_lines
    
    def getClosestTimestamp(self, timestamp): 
        if self.timestamps is None:
            self.getFull3dTrajectory() 
        return self.timestamps[np.argmin(np.abs(self.timestamps - timestamp))]

    def getFull3dTrajectory(self):
        num_lines = len(self.data)
        self.trajectory = []
        self.timestamps = []
        for ii in range(1,num_lines-1):
            try: 
                timestamp,x,y,z,scale = self.getTimePoseAndAbsoluteScale(ii)
                #print(f'timestamp: {timestamp}, x: {x}, y: {y}, z: {z}, scale: {scale}')
                self.timestamps.append(timestamp)
                self.trajectory.append([x,y,z])
            except:
                pass
        self.timestamps = np.array(self.timestamps, dtype=np.float64)
        self.trajectory = np.array(self.trajectory, dtype=np.float32)
        return self.trajectory, self.timestamps
        

# read the ground truth from a simple file containining [x,y,z,scale,timestamp] lines
class SimpleGroundTruth(GroundTruth):
    def __init__(self, path, name, associations=None, start_frame_id=0, type = GroundTruthType.KITTI): 
        super().__init__(path, name, associations, start_frame_id, type)
        self.scale = kScaleSimple
        self.filename=path + '/' + name
        with open(self.filename) as f:
            self.data = f.readlines()
            self.found = True 
        if self.data is None:
            sys.exit('ERROR while reading groundtruth file: please, check how you deployed the files and if the code is consistent with this!') 

    # return timestamp,x,y,z,scale
    def getTimePoseAndAbsoluteScale(self, frame_id):
        frame_id+=self.start_frame_id
        ss = self.getDataLine(frame_id-1)
        x_prev = self.scale*float(ss[1])
        y_prev = self.scale*float(ss[2])
        z_prev = self.scale*float(ss[3])     
        ss = self.getDataLine(frame_id)
        timestamp = float(ss[0]) 
        x = self.scale*float(ss[1])
        y = self.scale*float(ss[2])
        z = self.scale*float(ss[3])
        abs_scale = np.sqrt((x - x_prev)*(x - x_prev) + (y - y_prev)*(y - y_prev) + (z - z_prev)*(z - z_prev))
        return timestamp,x,y,z,abs_scale 


class KittiGroundTruth(GroundTruth):
    def __init__(self, path, name, associations=None, start_frame_id=0, type = GroundTruthType.KITTI): 
        super().__init__(path, name, associations, start_frame_id, type)
        self.scale = kScaleKitti
        self.filename=path + '/poses/' + name + '.txt'   # N.B.: this may depend on how you deployed the groundtruth files 
        self.filename_timestamps = path + '/sequences/' + name + '/times.txt'
        with open(self.filename) as f:
            self.data = f.readlines()
            self.found = True 
        if self.data is None:
            sys.exit('ERROR while reading groundtruth file: please, check how you deployed the files and if the code is consistent with this!') 
        self.data_timestamps = None
        with open(self.filename_timestamps) as f:
            self.data_timestamps = f.readlines()
            self.found = True 
        if self.data_timestamps is None:
            sys.exit('ERROR while reading groundtruth file: please, check how you deployed the files and if the code is consistent with this!')             


    # return timestamp,x,y,z,scale
    def getTimePoseAndAbsoluteScale(self, frame_id):
        frame_id+=self.start_frame_id
        ss = self.getDataLine(frame_id-1)
        x_prev = self.scale*float(ss[3])
        y_prev = self.scale*float(ss[7])
        z_prev = self.scale*float(ss[11])     
        ss = self.getDataLine(frame_id) 
        x = self.scale*float(ss[3])
        y = self.scale*float(ss[7])
        z = self.scale*float(ss[11])
        abs_scale = np.sqrt((x - x_prev)*(x - x_prev) + (y - y_prev)*(y - y_prev) + (z - z_prev)*(z - z_prev))

        timestamp = float(self.data_timestamps[frame_id].strip())
            
        return timestamp,x,y,z,abs_scale 


class TumGroundTruth(GroundTruth):
    def __init__(self, path, name, associations=None, start_frame_id=0, type = GroundTruthType.TUM): 
        super().__init__(path, name, associations, start_frame_id, type)
        self.scale = kScaleTum 
        self.filename=path + '/' + name + '/' + 'groundtruth.txt'     # N.B.: this may depend on how you deployed the groundtruth files 
        self.file_associations=path + '/' + name + '/' + associations # N.B.: this may depend on how you name the associations file
        
        base_path = os.path.dirname(self.filename)
        print('base_path: ', base_path)
                
        with open(self.filename) as f:
            self.data = f.readlines()[3:] # skip the first three rows, which are only comments 
            self.data = [line.strip().split() for line in  self.data] 
        if self.data is None:
            sys.exit('ERROR while reading groundtruth file!') 
        if self.file_associations is not None: 
            with open(self.file_associations) as f:
                self.associations = f.readlines()
                self.associations = [line.strip().split() for line in self.associations] 
            if self.associations is None:
                sys.exit('ERROR while reading associations file!')   
                
        associations_file = base_path + '/gt_associations.json'
        if not os.path.exists(associations_file):
            Printer.orange('Computing groundtruth associations (one-time operation)...')             
            self.association_matches = self.associate(self.associations, self.data)
            # save associations
            with open(associations_file, 'w') as f:
                json.dump(self.association_matches, f)
        else: 
            with open(associations_file, 'r') as f:
                data = json.load(f)
                self.association_matches = {int(k): v for k, v in data.items()}

    def getDataLine(self, frame_id):
        #return self.data[self.association_matches[frame_id][1]]
        return self.data[self.association_matches[frame_id][0]]

    # return timestamp,x,y,z,scale
    def getTimePoseAndAbsoluteScale(self, frame_id):
        frame_id+=self.start_frame_id
        ss = self.getDataLine(frame_id-1) 
        x_prev = self.scale*float(ss[1])
        y_prev = self.scale*float(ss[2])
        z_prev = self.scale*float(ss[3])     
        ss = self.getDataLine(frame_id)
        timestamp = float(ss[0]) 
        x = self.scale*float(ss[1])
        y = self.scale*float(ss[2])
        z = self.scale*float(ss[3])
        abs_scale = np.sqrt((x - x_prev)*(x - x_prev) + (y - y_prev)*(y - y_prev) + (z - z_prev)*(z - z_prev))
        return timestamp,x,y,z,abs_scale 
        #return timestamp,-x,-y,-z,abs_scale
    
    @staticmethod
    def associate(first_list, second_list, offset=0, max_difference=0.025*(10**9)):
        """
        Associate two dictionaries of (stamp,data). As the time stamps never match exactly, we aim 
        to find the closest match for every input tuple.
        
        Input:
        first_list -- first list of (stamp,data) tuples
        second_list -- second list of (stamp,data) tuples
        offset -- time offset between both dictionaries (e.g., to model the delay between the sensors)
        max_difference -- search radius for candidate generation

        Output:
        matches -- map: index_stamp_first -> (index_stamp_second, diff_stamps, first_timestamp, second_timestamp)
        
        """
        potential_matches = [(abs(float(a[0]) - (float(b[0]) + offset)), ia, ib) # a[0] and b[0] extract the first element which is a timestamp 
                            for ia,a in enumerate(first_list)      #for counter, value in enumerate(some_list)
                            for ib,b in enumerate(second_list)
                            if abs(float(a[0])  - (float(b[0])  + offset)) < max_difference]
        potential_matches.sort()
        matches = {}
        first_flag = [False]*len(first_list)
        second_flag = [False]*len(second_list)
        for diff, ia, ib in potential_matches:
            if first_flag[ia] is False and second_flag[ib] is False:
                #first_list.remove(a)
                first_flag[ia] = True
                #second_list.remove(b)
                second_flag[ib] = True 
                matches[ia]= (ib, diff, first_list[ia][0], second_list[ib][0])
        missing_associations = [(ia,a) for ia,a in enumerate(first_list) if first_flag[ia] is False]
        num_missing_associations = len(missing_associations)
        if num_missing_associations > 0:
            Printer.red(f'ERROR: {num_missing_associations} missing associations!')
        return matches       


class EurocGroundTruth(GroundTruth):
    def __init__(self, path, name, associations=None, start_frame_id=0, type = GroundTruthType.EUROC): 
        super().__init__(path, name, associations, start_frame_id, type)
        self.scale = kScaleEuroc
        self.filename = path + '/' + name + '/mav0/state_groundtruth_estimate0/data.tum'   # N.B.: Use the script groundtruth/generate_euroc_groundtruths_as_tum.sh to generate these groundtruth files
        
        base_path = os.path.dirname(self.filename)
        print('base_path: ', base_path)
        
        if not os.path.isfile(self.filename):
            Printer.red(f'Groundtruth file not found: {self.filename}')
                                    
        with open(self.filename) as f:
            self.data = f.readlines()
            self.data = [line.strip().split() for line in self.data] 
                    
        if len(self.data) > 0:
            self.found = True
            print('Processing Euroc groundtruth of lenght: ', len(self.data))
                
        if len(self.data) == 0:
            sys.exit(f'ERROR while reading groundtruth file {self.filename}: please, check how you deployed the files and if the code is consistent with this!') 
                    
        self.image_left_csv_path = path + '/' + name + '/mav0/cam0/data.csv'
        self.image_data=self.read_image_data(self.image_left_csv_path)
                            
        associations_file = base_path + '/associations.json'
        if not os.path.exists(associations_file):
            Printer.orange('Computing groundtruth associations (one-time operation)...')             
            self.association_matches = self.associate(self.image_data, self.data)
            # save associations
            with open(associations_file, 'w') as f:
                json.dump(self.association_matches, f)
        else: 
            with open(associations_file, 'r') as f:
                data = json.load(f)
                self.association_matches = {int(k): v for k, v in data.items()}

    def read_gt_data(self, csv_file):
        data = []
        # check csv_file exists 
        if not os.path.isfile(csv_file):
            Printer.red(f'Groundtruth file not found: {csv_file}')
            return []
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header row
            for row in reader:
                timestamp_ns = int(row[0])
                x = row[1]
                y = row[2]
                z = row[3]
                timestamp_s = (timestamp_ns / 1000000000)
                data.append((timestamp_s, (x,y,z)))
        return data
    
    def read_image_data(self, csv_file):
        timestamps_and_filenames = []
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header row
            for row in reader:
                timestamp_ns = int(row[0])
                filename = row[1]
                timestamp_s = (timestamp_ns / 1000000000)
                timestamps_and_filenames.append((timestamp_s, filename))
        return timestamps_and_filenames    
    
    @staticmethod
    def associate(first_list, second_list, offset=0, max_difference=0.025*(10**9)):
        """
        Associate two dictionaries of (stamp,data). As the time stamps never match exactly, we aim 
        to find the closest match for every input tuple.
        
        Input:
        first_list -- first list of (stamp,data) tuples
        second_list -- second list of (stamp,data) tuples
        offset -- time offset between both dictionaries (e.g., to model the delay between the sensors)
        max_difference -- search radius for candidate generation

        Output:
        matches -- map index_stamp_first -> (index_stamp_second, diff_stamps)
        
        """
        potential_matches = [(abs(float(a[0]) - (float(b[0]) + offset)), ia, ib) # a[0] and b[0] extract the first element which is a timestamp 
                            for ia,a in enumerate(first_list)      #for counter, value in enumerate(some_list)
                            for ib,b in enumerate(second_list)
                            if abs(float(a[0])  - (float(b[0])  + offset)) < max_difference]
        potential_matches.sort()
        matches = {}
        first_flag = [False]*len(first_list)
        second_flag = [False]*len(second_list)
        for diff, ia, ib in potential_matches:
            if first_flag[ia] is False and second_flag[ib] is False:
                #first_list.remove(a)
                first_flag[ia] = True
                #second_list.remove(b)
                second_flag[ib] = True 
                matches[ia]= (ib, diff)
        missing_associations = [(ia,a) for ia,a in enumerate(first_list) if first_flag[ia] is False]
        num_missing_associations = len(missing_associations)
        if num_missing_associations > 0:
            Printer.red(f'ERROR: {num_missing_associations} missing associations!')
        return matches   
        
    def getDataLine(self, frame_id):
        return self.data[self.association_matches[frame_id][0]]
    
    def getTimePoseAndAbsoluteScale(self, frame_id):
        frame_id+=self.start_frame_id
        ss = self.getDataLine(frame_id-1) 
        #print(f'ss[{frame_id-1}]: {ss}')
        x_prev = self.scale*float(ss[1])
        y_prev = self.scale*float(ss[2])
        z_prev = self.scale*float(ss[3])     
        ss = self.getDataLine(frame_id) 
        #print(f'ss[{frame_id}]: {ss}')  
        timestamp = float(ss[0])      
        x = self.scale*float(ss[1])
        y = self.scale*float(ss[2])
        z = self.scale*float(ss[3])
        abs_scale = np.sqrt((x - x_prev)*(x - x_prev) + (y - y_prev)*(y - y_prev) + (z - z_prev)*(z - z_prev))
        #print(f'abs_scale: {abs_scale}')
        # from https://www.researchgate.net/profile/Michael-Burri/publication/291954561_The_EuRoC_micro_aerial_vehicle_datasets/links/56af0c6008ae19a38516937c/The-EuRoC-micro-aerial-vehicle-datasets.pdf
        # WIP - not sure this is correct
        #return timestamp, y,z,-x, abs_scale   
        return timestamp, x,y,z, abs_scale