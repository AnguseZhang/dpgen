from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526.RunInstancesRequest import RunInstancesRequest
from aliyunsdkecs.request.v20140526.DeleteInstancesRequest import DeleteInstancesRequest
import time
import json
from dpgen.dispatcher.Batch import Batch
from dpgen.dispatcher.JobStatus import JobStatus
from dpgen.dispatcher.Shell import Shell
from dpgen.dispatcher.SSHContext import SSHContext, SSHSession

class ALI():
    def __init__(self, adata):
        self.ip_list = None
        self.regionID = None
        self.instance_list = None
        self.AccessKey_ID = adata["AccessKey_ID"]
        self.AccessKey_Secret = adata["AccessKey_Secret"]
        self.strategy = adata["pay_strategy"]
        self.pwd = adata["pwd"]

    def create_machine(self, instance_number, instance_type):
        if True:
            client = AcsClient(self.AccessKey_ID,self.AccessKey_Secret, 'cn-hangzhou')
            request = RunInstancesRequest()
            request.set_accept_format('json')
            request.set_UniqueSuffix(True)
            request.set_Password(self.pwd)
            request.set_Amount(instance_number)
            request.set_LaunchTemplateName(instance_type + '_cn-hangzhou_i')
            response = client.do_action_with_exception(request)
            response = json.loads(response)
            self.instance_list = response["InstanceIdSets"]["InstanceIdSet"]
            time.sleep(50)
            request = DescribeInstancesRequest()
            request.set_accept_format('json')
            request.set_InstanceIds(self.instance_list)
            response = client.do_action_with_exception(request)
            response = json.loads(response)

            ip = []
            for i in range(len(response["Instances"]["Instance"])):
                ip.append(response["Instances"]["Instance"][i]["PublicIpAddress"]['IpAddress'][0])
            self.ip_list = ip
            return self.ip_list, self.instance_list
        else:
            return "create failed"

    def delete_machine(self, instance_id):
        client = AcsClient(self.AccessKey_ID,self.AccessKey_Secret, 'cn-hangzhou')
        request = DeleteInstancesRequest()
        request.set_accept_format('json')
        request.set_InstanceIds(instance_id)
        request.set_Force(True)
        response = client.do_action_with_exception(request)

def run_ALI(stage, num_of_instance, adata):
    if stage == "train":
        instance_type = "ecs.gn5-c8g1.2xlarge"
    elif stage == "model_devi":
        instance_type = "ecs.gn5-c8g1.2xlarge"
    elif stage == "fp":
        instance_type = "ecs.c6.2xlarge"
    ali = ALI(adata)
    return ali.create_machine(num_of_instance, instance_type)

def exit_ALI(instance_id, adata):
    ali = ALI(adata)
    ali.delete_machine(instance_id)