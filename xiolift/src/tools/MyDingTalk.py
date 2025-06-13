from Tea.exceptions import TeaException
# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.

from alibabacloud_dingtalk.oauth2_1_0.client import Client as dingtalkoauth2_1_0Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dingtalk.oauth2_1_0 import models as dingtalkoauth_2__1__0_models
from alibabacloud_tea_util.client import Client as UtilClient

from alibabacloud_tea_util import models as util_models
from alibabacloud_dingtalk.drive_1_0.client import Client as dingtalkdrive_1_0Client
from alibabacloud_dingtalk.drive_1_0 import models as dingtalkdrive__1__0_models

from alibabacloud_dingtalk.storage_1_0.client import Client as dingtalkstorage_1_0Client
from alibabacloud_dingtalk.storage_1_0 import models as dingtalkstorage__1__0_models

from alibabacloud_dingtalk.wiki_2_0.client import Client as dingtalkwiki_2_0Client
from alibabacloud_dingtalk.wiki_2_0 import models as dingtalkwiki__2__0_models

from src.tools.Json import Json
import requests


class DingTalk:

    def __init__(self, app_key, app_secret, union_id):

        self.call_num = 0

        self.app_key = app_key
        self.app_secret = app_secret
        self.union_id = union_id

        self.auth_client = self.create_auth_client()
        self.drive_client = self.create_drive_client()
        self.storage_client = self.create_storage_client()
        self.wiki_client = self.create_wiki_client()

        self.access_token = self.get_access_token()


    @staticmethod
    def retry_with_new_token(func):
        """
        装饰器，用于处理因 access_token 过期导致的异常，并自动重试。
        """

        def wrapper(self, *args, **kwargs):

            try:
                return func(self, *args, **kwargs)

            except TeaException as err:
                # 处理access_token过期的错误

                if err.code == 'InvalidAuthentication':
                    if err.data.get('message') == '不合法的access_token':
                        print(f"Access token expired, refreshing token and retrying...")

                        # 重新获取新的access_token
                        self.access_token = self.get_access_token()

                        if self.access_token:
                            # 使用新的access_token重新执行原函数
                            return func(self, *args, **kwargs)
                        else:
                            print("Failed to refresh access token.")
                            return None
                else:
                    # 处理其他异常
                    print(f"An error occurred: {err}")
                    return None

            except Exception as err:

                print(err)
                return None

        return wrapper

    @staticmethod
    def create_auth_client() -> dingtalkoauth2_1_0Client:
        """
        使用 Token 初始化账号Client
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config()
        config.protocol = 'https'
        config.region_id = 'central'
        return dingtalkoauth2_1_0Client(config)

    @staticmethod
    def create_drive_client() -> dingtalkdrive_1_0Client:
        """
        使用 Token 初始化账号Client
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config()
        config.protocol = 'https'
        config.region_id = 'central'
        return dingtalkdrive_1_0Client(config)

    @staticmethod
    def create_storage_client() -> dingtalkstorage_1_0Client:
        """
        使用 Token 初始化账号Client
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config()
        config.protocol = 'https'
        config.region_id = 'central'
        return dingtalkstorage_1_0Client(config)

    # 知识库
    @staticmethod
    def create_wiki_client() -> dingtalkwiki_2_0Client:
        """
        使用 Token 初始化账号Client
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config()
        config.protocol = 'https'
        config.region_id = 'central'
        return dingtalkwiki_2_0Client(config)

    def get_access_token(self):

        get_access_token_request = dingtalkoauth_2__1__0_models.GetAccessTokenRequest(
            app_key=self.app_key,
            app_secret=self.app_secret
        )

        try:

            ret = self.auth_client.get_access_token(get_access_token_request)

            self.call_num += 1

            r = ret.to_map()

            Json.print(r, flag='access_token')

            return r['body']['accessToken']

        except Exception as err:
            if not UtilClient.empty(err.code) and not UtilClient.empty(err.message):
                print(err)

            return None

    @retry_with_new_token
    def get_space_list(self):

        list_spaces_headers = dingtalkdrive__1__0_models.ListSpacesHeaders()
        list_spaces_headers.x_acs_dingtalk_access_token = self.access_token
        list_spaces_request = dingtalkdrive__1__0_models.ListSpacesRequest(
            union_id=self.union_id,
            space_type='org',
            max_results=50
        )

        ret = self.drive_client.list_spaces_with_options(
            list_spaces_request,
            list_spaces_headers,
            util_models.RuntimeOptions()
        )
        self.call_num += 1

        r = ret.to_map()

        Json.print(r, flag='space_list')

        return r

    def get_file_list(self, space_id):

        list_all_dentries_headers = dingtalkstorage__1__0_models.ListAllDentriesHeaders()
        list_all_dentries_headers.x_acs_dingtalk_access_token = self.access_token

        try:

            next_tokens = None

            dentries = []

            while True:

                if next_tokens:
                    option = dingtalkstorage__1__0_models.ListAllDentriesRequestOption(
                        next_token=next_tokens,
                        max_results=50
                    )

                    list_all_dentries_request = dingtalkstorage__1__0_models.ListAllDentriesRequest(
                        option=option,
                        union_id=self.union_id
                    )

                else:
                    list_all_dentries_request = dingtalkstorage__1__0_models.ListAllDentriesRequest(
                        union_id=self.union_id
                    )

                # 默认傎 = 最大值 = 50
                ret = self.storage_client.list_all_dentries_with_options(
                    space_id,
                    list_all_dentries_request,
                    list_all_dentries_headers,
                    util_models.RuntimeOptions()
                )
                self.call_num += 1

                r = ret.to_map()

                Json.print(r, flag='file_list')

                body = r['body']

                dentries += body['dentries']

                next_tokens_ = body.get('nextToken', None)

                if not next_tokens_:
                    break

                next_tokens = next_tokens_

            return dentries

        except Exception as err:
            if not UtilClient.empty(err.code) and not UtilClient.empty(err.message):
                print(err)

            return None

    @retry_with_new_token
    def get_file_download_info(
            self,
            space_id,
            dentry_id
    ):

        get_file_download_info_headers = dingtalkstorage__1__0_models.GetFileDownloadInfoHeaders()
        get_file_download_info_headers.x_acs_dingtalk_access_token = self.access_token
        get_file_download_info_request = dingtalkstorage__1__0_models.GetFileDownloadInfoRequest(
            union_id=self.union_id
        )

        r = self.storage_client.get_file_download_info_with_options(
            space_id,
            dentry_id,
            get_file_download_info_request,
            get_file_download_info_headers,
            util_models.RuntimeOptions()
        )
        self.call_num += 1

        r = r.to_map()

        Json.print(r, flag='file_download_info')

        return r['body']

    @retry_with_new_token
    def download(self, json_, file_):

        # 提取 URL 和 headers

        url = json_["headerSignatureInfo"]["resourceUrls"][0]
        headers = json_["headerSignatureInfo"]["headers"]

        # 发送 GET 请求
        response = requests.get(url, headers=headers)

        # 检查响应是否成功
        if response.status_code == 200:
            # 将内容写入本地文件
            with open(file_, 'wb') as file:
                file.write(response.content)

            print("文件下载完成")

            return True

        else:
            print(f"请求失败，状态码: {response.status_code}")
            return False

    @retry_with_new_token
    def get_wiki_list(self):

        list_workspaces_headers = dingtalkwiki__2__0_models.ListWorkspacesHeaders()
        list_workspaces_headers.x_acs_dingtalk_access_token = self.access_token

        wikis = []

        next_token = None

        while True:

            list_workspaces_request = dingtalkwiki__2__0_models.ListWorkspacesRequest(
                next_token=next_token,
                max_results=50,
                order_by='VIEW_TIME_DESC',
                # team_id='lHiicjNFM2iSFYSdz2iPuI8ZwiEiE',
                with_permission_role=False,
                operator_id=self.union_id
            )

            ret = self.wiki_client.list_workspaces_with_options(list_workspaces_request, list_workspaces_headers, util_models.RuntimeOptions())
            self.call_num += 1

            r = ret.to_map()

            Json.print(r, flag='wiki_list')

            body = r['body']

            for wiki in body['workspaces']:
                # 去掉个人空间
                if '的空间' not in wiki['name'] and '的知识库' not in wiki['name']:
                    wikis.append(wiki)

            next_token_ = body.get('nextToken', None)

            if next_token_ is None:
                break

            next_token = next_token_

        return wikis

    @retry_with_new_token
    def get_node_list(self, node_id):

        # 文档 -- 知识库 -- 知识库目录树管理 --  获取节点列表

        list_nodes_headers = dingtalkwiki__2__0_models.ListNodesHeaders()
        list_nodes_headers.x_acs_dingtalk_access_token = self.access_token

        next_token = None

        nodes = []

        while True:

            list_nodes_request = dingtalkwiki__2__0_models.ListNodesRequest(
                parent_node_id=node_id,
                next_token=next_token,
                max_results=50, # 最大值为50
                with_permission_role=False,
                operator_id=self.union_id
            )

            ret = self.wiki_client.list_nodes_with_options(list_nodes_request, list_nodes_headers, util_models.RuntimeOptions())
            self.call_num += 1

            r = ret.to_map()

            Json.print(r, flag='node_list')

            body = r['body']
            nodes += body['nodes']

            next_token_ = body.get('nextToken', None)

            if next_token_ is None:
                break

            next_token = next_token_

        return nodes

