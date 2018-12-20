执行猫眼电影代码需要注意的两点:

(1) 字体反爬的问题,  猫眼电影中的票房收入，用户观影等数字用了字体反爬技术, 是使用的stonefont字体,并且是woff文件格式,
需要根据网页源码下载一个woff文件， 并且改为base.woff， 方便与每次运行生成的woff文件做比较,在本例中是直接下载
http://vfile.meituan.net/colorstone/5db25f6cfa649c642fe844a9cde5050c2084.woff 并且改为base.woff, 并且通过到http://fontstore.baidu.com/static/editor/index.html
网站查看woff文件中数据和unicode值, 并且写死在代码中, 具体字体反爬可参考https://blog.csdn.net/baidu_32542573/article/details/82259865帖子


(2)爬取数据插入到mysql时, 在pymysql连接中，要加上use_unicode=True, charset="utf8", 如
db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='maoyan',use_unicode=True, charset="utf8"),
不然会出现UnicodeEncodeError: 'latin-1' codec can't encode characters in position 101-103: ordinal not in range(256)错误

(3) 在用pyecharts画图时, 出现ModuleNotFoundError: No module named 'pyecharts_snapshot'错误

 答: 在安装时指定pyecharts的版本号 pip install pyecharts==0.1.9.4,  如果直接用pip install pyecharts安装, 则会安装其他版本, 出现上述错误提示
    