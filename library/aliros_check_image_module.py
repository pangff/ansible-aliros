from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeImagesRequest
from ansible.module_utils.basic import *
import json
import os


def initClient(module):
   clt = client.AcsClient(module.params['AccessKeyID'], module.params['AccessKeySecret'], module.params['RegionId'])
   return clt

def checkImageState(clt,module):
    req = DescribeImagesRequest.DescribeImagesRequest();
    req.set_headers({'x-acs-region-id':module.params['RegionId']})
    req.set_accept_format('json')
    req.set_ImageId(module.params["ImageId"])
    result = clt.do_action(req)
    writeLog("checkImage",result);
    return json.loads(result);

def writeLog(tag,text):
    f = open(os.path.abspath(os.curdir)+'/image-create.log','a');
    f.write(tag+":"+text+"\n")

def clearLog():
    f = open(os.path.abspath(os.curdir)+'/image-create.log','w');
    f.write("")


def main():
    fields = {
        "AccessKeyID": {"required": True, "type": "str"},
        "AccessKeySecret": {"required": True, "type": "str"},
        "RegionId": {"required": True, "type": "str"},
        "ImageId": {"required": True, "type": "str"}
    }
    module = AnsibleModule(argument_spec=fields)
    clt = initClient(module);
    result = checkImageState(clt,module);
    if len(result["Images"]["Image"])>0:
        status = result["Images"]["Image"][0]["Status"];
    else:
        status=""

    while status!="Available":
        result = checkImageState(clt,module);
        if len(result["Images"]["Image"])>0:
            status = result["Images"]["Image"][0]["Status"];
        else:
            status=""
        writeLog("wait image Available","current status"+status);
        time.sleep(60)

    response = {"result":result,"status":"ok"}
    module.exit_json(changed=False, meta=response)


if __name__ == '__main__':
    main()


