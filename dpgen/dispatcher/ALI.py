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

regionID = ['cn-hangzhou', 'cn-beijing', 'cn-shanghai', 'cn-qingdao', 'cn-zhangjiakou', 'cn-huhehaote']
instancdType = {
    '4vCPU':'ecs.c6.xlarge',
    '8vCPU':'ecs.c6.2xlarge',
    '16vCPU':'ecs.c6.4xlarge',
    'GPU':'ecs.gn6v-c8g1.2xlarge'
}

class ALI():
    def __init__(self):
        self.ip_list = None
        self.regionID = None
        self.instance_list = None
    # 尝试进行创建，但不真正创建，相当于pre_check，需要传入要创建的实例数量，实例类型
    def pre_create(self, instance_number, instance_type):
        for i in range(6):
            client = AcsClient('LTAI4FwshjFwCTD7tFHmQfh1','Oea8lGGbpNM1Bw8UmSMu2Deft8ve7e', regionID[i])
            request = RunInstancesRequest()
            request.set_accept_format('json')
            # dryrun为true时不会真正创建实例
            request.set_DryRun(True)
            request.set_Password('975481DING!')
            request.set_Amount(instance_number)
            # 指定模板，模板命名规则：instanceType_regionID_可用区ID，如ecs.c6.large_cn-hangzhou_i，即表示杭州可用区g的ecs.c6.large实例
            # 现在能用的只有一个模板，ecs.c6.large_cn-hangzhou_i
            templateName = instance_type + regionID[i] + 'i'
            request.set_LaunchTemplateName(templateName)
            response = client.do_action_with_exception(request)
            response = json.loads(response)
            # 如果可以创建，就返回true，否则继续查询
            if response['Code'] == 'DryRunOperation':
                self.regionID = regionID[i]
                return templateName
                # 例子：ecs.c6.large_cn-hangzhou_i
                # 通过函数返回的结果来判断是否可以创建成功，即开头都是ecs
            else:
                continue
        return "all_failed"
            
            
    # 创建成功会返回实例的ip列表
    def create_machine(self, instance_number, instance_type):
        # pre_check实际上就是模板的名字
        pre_check = self.pre_create(instance_number, instance_type)
        # it imply that we can create instances in this region
        if self.regionID:
            client = AcsClient('LTAI4FwshjFwCTD7tFHmQfh1','Oea8lGGbpNM1Bw8UmSMu2Deft8ve7e', self.regionID)
            request = RunInstancesRequest()
            request.set_accept_format('json')
            request.set_UniqueSuffix(True)
            request.set_Password("975481DING!")
            request.set_Amount(instance_number)
            request.set_LaunchTemplateName(pre_check)
            response = client.do_action_with_exception(request)
            response = json.loads(response)
            # 获取实例ID
            InstanceId = response["InstanceIdSets"]["InstanceIdSet"]
            self.instance_list = InstanceId
            time.sleep(5)
            # 等待机器创建，获取ip地址
            request = DescribeInstancesRequest()
            request.set_accept_format('json')

            # 要查询的实例ID列表
            request.set_InstanceIds(InstanceId)
            response = client.do_action_with_exception(request)
            response = json.loads(response)

            # 获取当前实例的ip地址
            ip = []
            for i in range(len(response["Instances"]["Instance"])):
                ip.append(response["Instances"]["Instance"][i]["PublicIpAddress"]['IpAddress'])
            self.ip_list = ip
            return ip
        else:
            return "create failed"

    def delete_machine(self):
        client = AcsClient('LTAI4FwshjFwCTD7tFHmQfh1','Oea8lGGbpNM1Bw8UmSMu2Deft8ve7e', self.regionID)
        request = DeleteInstancesRequest()
        request.set_accept_format('json')
        request.set_InstanceIds(InstanceId)
        request.set_Force(True)
        response = client.do_action_with_exception(request)
        
