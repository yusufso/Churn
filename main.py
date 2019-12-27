import requests
import wget
import os

#https://9gag.com/v1/group-posts/group/video/type/hot&c=100
#URL = "https://9gag.com/v1/group-posts/group/video/type/hot?&c=20"
URL = "https://9gag.com/v1/group-posts/group/video/type/hot&c=500"

#JSON of nsfw: data>post>postid>nsfw
#JSON of URL: data>posts>postid>image>image460sv>h265Url
#JSON of duration: data>posts>postid>image>image460sv>duration

def requestPostUrls(inputUrl):
        #requesting videos container in json
        returnedVidsContainer = requests.get(inputUrl, {}).json()
        #getting individual posts from videos container
        allPosts = returnedVidsContainer["data"]["posts"]

        #getting urls for each post
        postObjects = []
        for post in allPosts:
                if post["type"] == "Animated":
                        postObjects.append(post)

        return postObjects

def getVideoUrls(inputPostObjs, minSumTime):
        sumTime = 0
        uneditedVidUrls = []
        
        for inputPostObj in inputPostObjs:
                inputPostImage = inputPostObj["images"]["image460sv"]
                inputPostUrl = inputPostImage["h265Url"]

                #if inputPost has audio AND the finalvideo length < 11 mins AND it isn't nsfw AND is mp4
                if (inputPostImage["hasAudio"] == 1) and (sumTime < minSumTime) and (inputPostObj["nsfw"] == 0) and (inputPostUrl[-3:] == "mp4"):
                        uneditedVidUrls.append(inputPostUrl)

        return uneditedVidUrls                


def downloadVideos(videoUrls):
        uneditedVidDirs = []
        vidIndex = 0

        for videoUrl in videoUrls:
                uneditedVidDir = "uneditedVideo" + str(vidIndex) + ".mp4"
                # wget.download(videoUrl, "/temp/uneditedVideo" + str(vidIndex) + ".mp4")
                wget.download(videoUrl, "./" + uneditedVidDir)
                uneditedVidDirs.append(uneditedVidDir)

                vidIndex = vidIndex + 1

        print("uneditedVidDirs: " + str(uneditedVidDirs))
        return uneditedVidDirs
        

##VIDEO EDITING##
def padVideos(videoDirs):
        padVidIndex = 0
        padVidDirs = []

        for videoToPad in videoDirs:
                os.system("ffmpeg -i " + videoToPad + " -filter:v \"scale=w=1920:h=1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1\" -crf 18 -preset faster -c:a copy paddedVideo" + str(padVidIndex) + ".mp4")
                padVideoDir = "./paddedVideo" + str(padVidIndex) + ".mp4"
                padVidDirs.append(padVideoDir)

                padVidIndex = padVidIndex + 1

        print("padVidDirs: " + str(padVidDirs))
        return padVidDirs

def concatVideos(paddedVideoDirs):
        ffmpegcmdConcat = "ffmpeg "
        for paddedVideoDir in paddedVideoDirs:
                ffmpegcmdConcat = ffmpegcmdConcat + "-i " + paddedVideoDir + " "
        
        ffmpegcmdConcat = ffmpegcmdConcat + "-y -filter_complex concat=n=" + str(len(paddedVideoDirs)) + ":v=1:a=1 finalVideo.mp4"
        os.system(ffmpegcmdConcat)

post = requestPostUrls(URL)
uneditedVidUrls = getVideoUrls(post, 600)
uneditedVidDirs = downloadVideos(uneditedVidUrls)
paddedVidDirs = padVideos(uneditedVidDirs)
concatVideos(paddedVidDirs)