# AWS Route Tables + Python JSON Object


**(1) AWS Route Tables**

* Boto3 script to show all route tables in VPC and Subnet in one shot
* Show VPC Peering targets as well as Internet GW or NAT GW targets


**(2) Python JSON Object**

* wrapper class to handle objects returned from web API
  - for example, `print(JsonObject(response))` to convert to JSON.
* by this class, you can use JavaScript style dot notation access
  - for example, `vpcs[0].Tags[0].Key` instead of `vpcs[0]["Tags"][0]["Key"]`


**Sample output**

```text
vpc-03b96307a33428987  cvpn_test_vpc_cvpn  10.0.0.0/16 (10.0.0.1-10.0.255.254) (owner_id: 100000000000)
  [rtb-05abd25320cfd90b9]  <Main route table>
  10.0.0.0/16   local

    subnet-0d4b9e1cf2223169a  cvpn_test_subnet_cvpn  us-west-2a  10.0.1.0/24 (10.0.1.1-10.0.1.254)
      [rtb-0edab5f8845653e29] cvpn_test_rt
      10.0.0.0/16   local
      10.10.0.0/16  vpc_peering: 100000000000|ap-northeast-1|vpc-085071b77f46b90cd|10.10.0.0/16

vpc-04da3256                               172.31.0.0/16 (172.31.0.1-172.31.255.254) (owner_id: 100000000000)
  [rtb-e50a5a34]  <Main route table>
  172.31.0.0/16 local
  0.0.0.0/0     igw-046c054d

    subnet-613079a6                                  us-west-2a  172.31.16.0/20 (172.31.16.1-172.31.31.254)
    subnet-a5d28191                                  us-west-2b  172.31.32.0/20 (172.31.32.1-172.31.47.254)
    subnet-05e9b155                                  us-west-2c  172.31.0.0/20 (172.31.0.1-172.31.15.254)
```


## Setup

```bash
brew install pyenv
brew install pipenv
export PIPENV_VENV_IN_PROJECT=true
pipenv install
```

* to initialize python environment

```bash
pipenv --python 3.6
pipenv install boto3
pipenv install black pylint pytest pytest-cov --dev
pipenv run pip list
pipenv graph
pipenv shell
```


## Test by Pytest

```bash
cd tests
PYTHONPATH=../src pipenv run pytest -v --cov=../src --cov-report=term-missing
```

* run with html coverage report

```bash
PYTHONPATH=../src pipenv run pytest -v --cov=../src --cov-report=html
```


## Run

```bash
pipenv run ./src/aws_route.py
```

* note: you might see same route table several times under different subnet
* use `--region_name` for region, `--profile_name` for profile

```bash
pipenv run ./src/aws_route.py --region_name us-west-2 --profile_name foo
```


## Reference

* https://qiita.com/draco/items/8b99e5494ec5b1371f32
* https://qiita.com/stkdev/items/e262dada7b68ea91aa0c
* https://wiki.python.org/moin/SubclassingDictionaries
* http://d.hatena.ne.jp/karasuyamatengu/20120408/1333862237
* https://portingguide.readthedocs.io/en/latest/core-obj-misc.html
* https://stackoverrun.com/ja/q/10460042
* https://gist.github.com/peterhurford/09f7dcda0ab04b95c026c60fa49c2a68
* https://stackoverflow.com/questions/16237659/python-how-to-implement-getattr
* http://thinkami.hatenablog.com/entry/2017/03/07/065903
* https://qiita.com/Mabuchin/items/161d33f845ec0aeeb777
