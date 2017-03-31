from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import CreateImageRequest,DescribeInstancesRequest,DescribeImagesRequest
from ansible.module_utils.basic import *
import json
import os


def initClient(module):
   clt = client.AcsClient(module.params['AccessKeyID'], module.params['AccessKeySecret'], module.params['RegionId'])
   return clt

def createImage(clt,module,InstanceId):
    req = CreateImageRequest.CreateImageRequest();
    req.set_headers({'x-acs-region-id':module.params['RegionId']})
    req.set_accept_format('json')
    req.set_ImageName("china-net-server-image")
    req.set_InstanceId(InstanceId)
    result = clt.do_action(req)
    writeLog("createImage",result);
    return json.loads(result);

def getInstances(clt,module):
    req = DescribeInstancesRequest.DescribeInstancesRequest();
    req.set_headers({'x-acs-region-id':module.params['RegionId']})
    req.set_accept_format('json')
    result = clt.do_action(req)
    writeLog("createImage-getInstances",result);
    return json.loads(result);

def getCreatedInstnceIpByName(instances):
    ip = ""
    InstanceId="";
    for item in instances["Instances"]["Instance"]:
        if item["InstanceName"] == "china-net-server-instance":
            ip=item["PublicIpAddress"]["IpAddress"]
            InstanceId=item["InstanceId"]
            break;
    return {"ip":ip[0],"InstanceId":InstanceId};

def writeLog(tag,text):
    f = open(os.path.abspath(os.curdir)+'/image-create.log','a');
    f.write(tag+":"+text+"\n")

def clearLog():
    f = open(os.path.abspath(os.curdir)+'/image-create.log','w');
    f.write("")

def saveImageId(imageId):
    f = open(os.path.abspath(os.curdir)+'/config/created-imageId.txt','w');
    f.write(imageId)

def main():
    fields = {
        "AccessKeyID": {"required": True, "type": "str"},
        "AccessKeySecret": {"required": True, "type": "str"},
        "RegionId": {"required": True, "type": "str"}
    }
    module = AnsibleModule(argument_spec=fields)
    clt = initClient(module);
    instances = getInstances(clt,module);
    instance = getCreatedInstnceIpByName(instances);
    result=createImage(clt,module,instance["InstanceId"]);
    response = {"result":result,"status":"ok"}
    saveImageId(result["ImageId"]);
    module.exit_json(changed=False, meta=response)


if __name__ == '__main__':
    main()


