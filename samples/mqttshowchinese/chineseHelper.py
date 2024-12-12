import gb2312

class chineseHelper(object):
    def __init__(self):
        self.f = open('hzk16h', 'rb')
    
    def GetHzCode(self, message):
        gbdata = gb2312.fontbyte.strs(message)
        return self.GetHzCodeInternal(gbdata)
    
    def GetHzCodeInternal(self, gbdata):
        datas = []
        i = 0
        while i < len(gbdata):
            f = gbdata[i] - 0xa0
            s = gbdata[i+1] - 0xa0
            offset = (94 * (f - 1) + (s - 1)) * 32
            self.f.seek(offset ,0)
            datas.append(self.f.read(32))
            i+=2
        return datas
    
    def __del__(self):
        self.f.close()
        
instance = chineseHelper()