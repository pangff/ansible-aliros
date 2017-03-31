from aliyunsdkcore import client
from aliyunsdkros.request.v20150901 import DeleteStackRequest
from ansible.module_utils.basic import *


def initClient(module):
   clt = client.AcsClient(module.params['AccessKeyID'], module.params['AccessKeySecret'], module.params['RegionId'])
   return clt



def deleteCreatedStackInfoRos(clt,module):
    req =DeleteStackRequest.DeleteStackRequest()
    req.set_StackName(module.params["StackName"])
    req.set_StackId(module.params["StackId"])
    req.set_headers({'x-acs-region-id':module.params['RegionId']})
    status, headers, body = clt.get_response(req)
    if status == 204:
         return {"message":"delete success"};
    else:
        print('Unexpected errors: status=%d, error=%s' % (status, body))
        return "None";



def main():
    fields = {
        "AccessKeyID": {"required": True, "type": "str"},
        "AccessKeySecret": {"required": True, "type": "str"},
        "RegionId": {"required": True, "type": "str"},
        "StackId": {"required": True, "type": "str"},
        "StackName": {"required": True, "type": "str"}
    }
    module = AnsibleModule(argument_spec=fields)
    clt = initClient(module);
    result = deleteCreatedStackInfoRos(clt,module);
    response = {"result":result,"status":"ok"}
    module.exit_json(changed=False, meta=response)



if __name__ == '__main__':
    main()


