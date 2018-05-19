#!/usr/bin/python

'''
/*
 * @File: clonerepo.py
 * @Author: Arunkumar Sadasivan
 * @Date: 04/05/2018
 * @Description: Clone all repo's that belong to a group or organization. Repo's can be segregated based on the branch.
 * @Usage: clonerepo.py
 * @Dependecies: python 3.6   
 */
 
'''

import os
import requests
import subprocess
import shutil # create zip file


# Defaults
gitBaseURL= "https://gitlab-uri/api/v4/"

def initiateGETRequest(URL):
    try:
        response = requests.get(URL) 
        return response       
    except (requests.exceptions.HTTPError,requests.exceptions.ConnectTimeout,requests.exceptions.ConnectionError) as e:
        print (e)

def getGitlabGroupId(groupName, personalToken):
    URL = gitBaseURL + "groups?search=" + groupName + "&private_token=" + personalToken 
    response = initiateGETRequest(URL)
    if response.status_code == 200:
        return response.json()[0]["id"]
    else:
        errorMsg = "[Error] Error occurred while trying to get GIT Group ID"
        print(errorMsg)   

# get all git repos that belong to  a group     
def getGitlabRepos(GroupId, personalToken):
    URL = gitBaseURL + "groups/" + GroupId + "?private_token=" + personalToken 
    httpURLRepoDict = {} #key => repoName values => [repoId, repoHTTPURL]
    response = initiateGETRequest(URL)
    if response.status_code == 200: 
        reposArry = response.json()["projects"]
        for repo in reposArry:
            httpURLRepoDict[repo["name"]] = [repo["id"], repo["http_url_to_repo"]]
        return httpURLRepoDict
    else:
        errorMsg = "[Error] Error occurred while trying to get repos from GIT"
        print(errorMsg)   

#  check if repo contains branch       
def checkRepoBranchExists(repoName, repoId, personalToken, branchName):
    URL = "".join([gitBaseURL + "projects/", repoId, "/repository/branches/", branchName, "?private_token=", personalToken]) 
    response = initiateGETRequest(URL)
    if response.status_code == 200:
        return True     
    else:
        print("[Error] Branch:" + branchName + " does not exists for " + repoName)
        return False       
     
        
# run git clone command        
def gitClone(repo, branchName, personalToken, userName):
    repo = repo.replace("https://","https://" + userName + ":" + personalToken + "@")
    gitCommand = "git clone -b " + branchName + " " + repo
    try:
        subprocess.run(gitCommand,check=True,shell=True)
    except subprocess.CalledProcessError as err:
        print("[ERROR] Error occurred while trying to run git clone command", err)
        
# Create directory if it doesn't exist
def checkDirExists(path):
    if not os.path.exists(path): # check directory exists 
        os.makedirs(path) # create directory         


# clone all repos that belong to a group 
def createSourceRepo(groupName, personalToken, branchName, userName):
    groupId = getGitlabGroupId(groupName, personalToken)
    httpURLrepoDict = getGitlabRepos(str(groupId), personalToken) 
    #cwd = os.getcwd()
    checkDirExists(groupName)
    os.chdir(groupName)
    for repoName, repoInfo in httpURLrepoDict.items():
        repoId = repoInfo[0]
        repoURL = repoInfo[1]
        if checkRepoBranchExists(repoName, str(repoId), personalToken, branchName):
            gitClone(repoURL, branchName, personalToken, userName)       
    #archivename = createSourceRepoZip (groupName,cwd)
    #return archivename
    
# create zip file    
def createGitRepoZip (groupName, personalToken, branchName):
    createSourceRepo(groupName, personalToken, branchName)
    os.chdir("..")
    cwd = os.getcwd()
    print("[Info] Archiving " + groupName)
    base_name = cwd + "/" + groupName
    fileType = "zip"
    root_dir = cwd + "/" + groupName
    # shutil.make_archive(base_name,format,root_dir,base_dir)
    archivename = shutil.make_archive(base_name, fileType, root_dir)
    print("[Success] " + archivename + " successfully created.")
    return archivename


groupname = "groupname"
branchname = "master"
gitpersonalToken = "**************"
createSourceRepo(groupname, gitpersonalToken, branchname, userName)

