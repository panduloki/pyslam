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


'''
List of shared parameters 
''' 
class Parameters(object):   
    
    # SLAM threads 
    kLocalMappingOnSeparateThread=True           # True: move local mapping on a separate thread, False: tracking and then local mapping in a single thread 
    kTrackingWaitForLocalMappingToGetIdle=False  
    kTrackingWaitForLocalMappingSleepTimeStereo=0.1 #      -1 for no sleep # [s]    (NOTE: a bit of sleep time increases the call rate of LBA and therefore VO accuracy)
    kTrackingWaitForLocalMappingSleepTimeMono=0.1   #0.6 # -1 for no sleep # [s]    (NOTE: a bit of sleep time increases the call rate of LBA and therefore VO accuracy)
    kLocalMappingParallelKpsMatching=True
    kLocalMappingParallelKpsMatchingNumWorkers=6
    
    
    # Number of desired keypoints per frame 
    kNumFeatures=2000
    

    # Point triangulation 
    kCosMaxParallaxInitializer=0.99998  # 0.99998   # max cos angle for triangulation (min parallax angle) in the Initializer
    kCosMaxParallax=0.9999 # 0.9998                 # max cos angle for triangulation (min parallax angle)   
    
    
    # Point visibility 
    kViewingCosLimitForPoint=0.5    # must be viewing cos < kViewingCosLimitForPoint (viewing angle must be less than 60 deg)
    kScaleConsistencyFactor=1.5
    kMaxDistanceToleranceFactor=1.2 
    kMinDistanceToleranceFactor=0.8   


    # Feature management
    kSigmaLevel0 = 1.0                        # sigma of the keypoint localization at level 0 (default value is 1 for ORB detector); can be changed by selected feature    
    kFeatureMatchRatioTest = 0.7              
    #kFeatureMatchRatioTestInitializer        # ratio test used by Initializer 
    #
    kKdtNmsRadius = 3 # pixels  #3            # radius for kd-tree based Non-Maxima Suppression
    #
    kCheckFeaturesOrientation = True 


    # Initializer 
    kInitializerDesiredMedianDepth = 20    # when initializing, the initial median depth is computed and forced to this value (for better visualization is > 1) 
    kMinRatioBaselineDepth = 0.01 
    #kMinTraslation = 0.01*kInitializerDesiredMedianDepth  # not used at the present time     
    kInitializerNumMinFeatures = 100
    kInitializerNumMinFeaturesStereo = 500
    kInitializerNumMinTriangulatedPoints = 150
    kFeatureMatchRatioTestInitializer = 0.9   # ratio test used by Initializer       
    kInitializerNumMinNumPointsForPnPWithDepth = 15 


    # Tracking 
    kUseMotionModel = True                            # use or not the motion model for computing a first guess pose (that will be optimized by pose optimization)  
    kUseSearchFrameByProjection = True                # match frames by using frame map points projection and epipolar lines; here, the current available interframe pose estimate is used for computing the fundamental mat F
    kMinNumMatchedFeaturesSearchFrameByProjection=20  # if the number of tracked features is below this, then the search fails 
    kUseEssentialMatrixFitting = False                # fit an essential matrix; orientation and keypoint match inliers are estimated by fitting an essential mat (5 points algorithm), 
                                                      # WARNING: essential matrix fitting comes with some limitations (please, read the comments of the method slam.estimate_pose_ess_mat())
    kMaxNumOfKeyframesInLocalMap = 80
    kNumBestCovisibilityKeyFrames = 10
    kUseVisualOdometryPoints = True
    
    # Keyframe generation 
    kNumMinPointsForNewKf = 15                               # minimum number of matched map points for spawning a new KeyFrame 
    kNumMinTrackedClosePointsForNewKfNonMonocular = 100      # minimum number of tracked close map points that for not spawning a new KeyFrame in case of a non-monocular system
    kNumMaxNonTrackedClosePointsForNewKfNonMonocular = 70    # maximum number of non-tracked close map points for not spawning a new KeyFrame in case of a non-monocular system    
    kThNewKfRefRatio = 0.9                                   # for determining if a new KF must be spawned, condition 3
    kThNewKfRefRatioStereo = 0.75                            # for determining if a new KF must be spawned, condition 3, in the case non-monocular
    kThNewKfRefRatioNonMonocualar = 0.25                     # for determining if a new KF must be spawned in case the system is not monocular, condition 2b
    
    # Keyframe culling
    kKeyframeCullingRedundantObsRatio = 0.9  
    kKeyframeMaxTimeDistanceInSecForCulling = 0.5 # [s]  # Use float('inf') for disabling it   
    kKeyframeCullingMinNumPoints = 50 

    # Stereo matching 
    kStereoMatchingMaxRowDistance = 1.5       # [pixels] 
    kStereoMatchingShowMatchedPoints = False   # show the frame stereo matches (debug stereo matching)

    # Search matches by projection 
    kMaxReprojectionDistanceFrame = 7    #7   # [pixels]    o:7
    kMaxReprojectionDistanceMap = 3      #3   # [pixels]    o:1,(rgbd)3,(reloc)5 => mainly 2.5*th where th acts as a multiplicative factor 
    kMaxReprojectionDistanceMapRgbd = 5  #5   # [pixels]    o:5
    kMaxReprojectionDistanceFuse = 3     #3   # [pixels]    o:3
    #
    kMatchRatioTestMap=0.8
    kMatchRatioTestEpipolarLine=0.8      # used just for test function find_matches_along_line()
    #
    # Reference max descriptor distance (used for initial checks and then updated and adapted)                   
    kMaxDescriptorDistance=0 # it is updated by feature_manager.py at runtime 
    

    # Search matches for triangulation by using epipolar lines 
    kMinDistanceFromEpipole=10                  # [pixels] Used with search by epipolar lines 
    #
    kMaxDescriptorDistanceSearchEpipolar=0 # it is updated by feature_manager.py at runtime 


    # Local Mapping 
    kLocalMappingNumNeighborKeyFrames=20                   #  [# frames]   for generating new points and fusing them              


    # Covisibility graph 
    kMinNumOfCovisiblePointsForCreatingConnection=15 
    
    
    # Bundle Adjustment (BA)
    kLocalBAWindow=20                 #  [# frames]   
    kUseLargeWindowBA=False           # True: perform BA over a large window; False: do not perform large window BA       
    kEveryNumFramesLargeWindowBA=10   # num of frames between two large window BA  
    kLargeBAWindow=20                 #  [# frames] 
        
    
    # Pointcloud 
    kColorPatchDelta=1  # center +- delta


    # other parameters 
    kChi2Mono = 5.991 # chi-square 2 DOFs, used for reprojection error  (Hartley Zisserman pg 119)
    kChi2Stereo = 7.815 # chi-square 3 DOFs, used for reprojection error  (Hartley Zisserman pg 119)

