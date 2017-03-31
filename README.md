# 使用ansible、Ros创建ecs,安装git、node、npm、clone代码后创建镜像、释放ecs

* 修改roles/*/defaults/main.ml中相关阿里云信息配置
* 运行

```
ansible-playbook aliros-create-deploy.yml

```

运行时间较长，中途会要求输入一次用户名、密码。运行完成会在config/created-imageId.txt下添加创建后的镜像id

# 根据上面创建的镜像通过Ros批量创建ecs，并添加到指定SLB下

* 修改roles/*/defaults/main.ml中相关阿里云信息配置
* 运行

```
ansible-playbook aliros-ecs-clone-set-slb.yml

```
