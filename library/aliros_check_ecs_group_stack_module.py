from aliyunsdkcore import client
from aliyunsdkros.request.v20150901 import DescribeResourcesRequest, CreateStacksRequest,DescribeStackDetailRequest
from ansible.module_utils.basic import *
import json
import time
import os
import yaml


def initClient(module):
   clt = client.AcsClient(module.params['AccessKeyID'], module.params['AccessKeySecret'], module.params['RegionId'])
   return clt

def createStackByRos(clt,module):
    imageId = readImageId();
    template = '''
    {
        "ROSTemplateFormatVersion": "2015-09-01",
        "Resources": {
            "My_ECS_InstanceGroup": {
                "Type" : "ALIYUN::ECS::InstanceGroup",
                "Description": "Create a ECS instance for demo.",
                "Properties": {
                    "ImageId":"%s",
                    "MaxAmount":%s,
                    "MinAmount":%s,
                    "InstanceType": "ecs.t1.small",
                    "InternetChargeType": "PayByTraffic",
                    "Password":"Password123",
                    "IoOptimized": "none",
                    "SystemDisk_Category": "cloud",
                    "SecurityGroupId": {
                        "Fn::GetAtt": [
                            "mySecurityGroup",
                            "SecurityGroupId"
                        ]
                    }
                }
            },

            "mySecurityGroup": {
                "Type": "ALIYUN::ECS::SecurityGroup",
                "Properties": {
                    "SecurityGroupName": "ecsInstanceSecurity",
                    "SecurityGroupIngress": [{
                        "SourceCidrIp": "0.0.0.0/0",
                        "IpProtocol": "all",
                        "NicType": "internet",
                        "PortRange": "-1/-1",
                        "Priority": 1
                      },{
                        "SourceCidrIp": "0.0.0.0/0",
                        "IpProtocol": "all",
                        "NicType": "intranet",
                        "PortRange": "-1/-1",
                        "Priority": 1
                      }],
                    "SecurityGroupEgress": [{
                        "IpProtocol": "all",
                        "DestCidrIp": "0.0.0.0/0",
                        "NicType": "internet",
                        "PortRange": "-1/-1",
                        "Priority": 1
                      },{
                        "IpProtocol": "all",
                        "DestCidrIp": "0.0.0.0/0",
                        "NicType": "intranet",
                        "PortRange": "-1/-1",
                        "Priority": 1
                      }]
                }
            },
            "AttachmentSLB": {
              "Type": "ALIYUN::SLB::BackendServerAttachment",
              "Properties": {
                "LoadBalancerId": "%s",
                "BackendServerList": {
                    "Fn::GetAtt": [
                        "My_ECS_InstanceGroup",
                        "InstanceIds"
                    ]
                }
              }
            }
        }
    }
    ''' % (imageId,module.params["EcsCount"],module.params["EcsCount"],module.params["SLBId"])

    create_stack_body = '''
    {
        "Name": "%s",
        "TimeoutMins": %d,
        "Template": %s
    }
    ''' % ('createEcsStack', 60, template)

    req = CreateStacksRequest.CreateStacksRequest()
    req.set_headers({'x-acs-region-id':module.params['RegionId']})
    req.set_content(create_stack_body);

    status, headers, body = clt.get_response(req)
    writeLog("createStackByRos",body);
    if status == 201:
         result = json.loads(body)
         return result;
    else:
        return "None";


def getCreatedStackInfoRos(clt,stack):
    req =DescribeStackDetailRequest.DescribeStackDetailRequest()
    req.set_StackName(stack["Name"])
    req.set_StackId(stack["Id"]);
    status, headers, body = clt.get_response(req)
    writeLog("getCreatedStackInfoRos",body);
    if status == 200:
         result = json.loads(body)
         return result;
    else:
        return "None";


def checkResourcesIsCreateComplete(stackInfo):
    if stackInfo['Status'] == "CREATE_COMPLETE":
        return "true"
    else:
        return "false"

def writeLog(tag,text):
    f = open(os.path.abspath(os.curdir)+'/ecs-clone.log','a');
    f.write(tag+":"+text+"\n")

def clearLog():
    f = open(os.path.abspath(os.curdir)+'/ecs-clone.log','w');
    f.write("")

def readImageId():
    f = open(os.path.abspath(os.curdir)+'/config/created-imageId.txt','r');
    return f.read()


def main():
    clearLog();
    fields = {
        "AccessKeyID": {"required": True, "type": "str"},
        "AccessKeySecret": {"required": True, "type": "str"},
        "RegionId": {"required": True, "type": "str"},
        "EcsCount": {"required": True, "type": "str"},
        "SLBId": {"required": True, "type": "str"}
    }
    module = AnsibleModule(argument_spec=fields)
    clt = initClient(module);
    stock = createStackByRos(clt,module);
    if stock=="None" :
        response = {"result":"create stock error","status":"error"}
        module.exit_json(changed=False, meta=response)

    result = getCreatedStackInfoRos(clt,stock);

    if result=="None" :
        response = {"result":"get stock resources error","status":"error"}
        module.exit_json(changed=False, meta=response)

    while (checkResourcesIsCreateComplete(result) != "true"):
        time.sleep(5)
        result=getCreatedStackInfoRos(clt,stock)

    response = {"status":"ok","result":stock}
    module.exit_json(changed=False, meta=response)


if __name__ == '__main__':
    main()


