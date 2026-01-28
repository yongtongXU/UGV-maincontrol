'''
用于生成JS代码
'''


def getBaseJS():
    """
    JS起始函数 随便写
    :return:
    """
    base_js_str = '''
          function refreshMap()
          {
            // mark placeholder
            
            // planPath placeholder
            
            // trackPath placeholder
          }
          refreshMap();
          '''
    return base_js_str

def getClearJS():
    """
        JS起始函数 随便写
        :return:
        """
    clear_js_str = '''
              function refreshMap()
              {
                map.removeOverlay(robotMark);
                map.removeOverlay(planPolyline);
                map.removeOverlay(trackPolyline);
              }
              refreshMap();
              '''
    return clear_js_str

def getMapTouchJS():
    touch_js_str = '''
          function getTouchMap()
          {
            var backPoint = shareForPyLatLon;
            shareForPyLatLon = '';
            return backPoint;
          }
          getTouchMap();
          '''
    return touch_js_str

def add_markMap_JS(lon_lat,mark_num):
    
    add_markMap_JS_str = '''
       
       function addMarker() {
             
        var marker_add = new AMap.Marker({
            position: new AMap.LngLat(mark_str),
            icon: "https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png",
            offset: new AMap.Pixel(-13, -30),
            title:'mark_num'
        });
        //map.add(marker_add);
        marker_add.setMap(map);
        document.querySelector("#info_text").innerText = "mark_str";
        marker_add_num += 1;
        marker_add_all.push(marker_add);
        return marker_add_num;
    } 
    addMarker();
    '''
    mark_str = lon_lat
    mark_data_str = add_markMap_JS_str.replace("mark_str", mark_str)
    mark_data_str = mark_data_str.replace("mark_num", str(mark_num))
    return mark_data_str

def del_markMap_JS():
    del_markMap_JS_str = '''
    function del_Marker(){
    marker_add_all[marker_add_all.length - 1].setMap(null);
    marker_add_all.pop();
    marker_add_num -= 1;
    }
    del_Marker();
    '''
    return del_markMap_JS_str

def clear_markMap_JS():
    clear_markMap_JS_str = '''
    function clear_Marker(){
    map.remove(polyline);
    for (var i=marker_add_all.length-1;i>=0;i--){ 
    marker_add_all[i].setMap(null);
    marker_add_all.pop();
    }
    }
    clear_Marker();
    '''
    return clear_markMap_JS_str

def path_markMap_JS(marker_list):
    path_markMap_JS_str = '''
    
    function path_markMap(){
    var path = marker_list;
    polyline = new AMap.Polyline({
    path: path,
    isOutline: false,
    
    borderWeight: 1,
    strokeColor: "#3366FF",
    strokeOpacity: 1,
    strokeWeight: 2,
    strokeStyle: "dashed",
    strokeDasharray: [10, 5],
    lineJoin: 'round',
    lineCap: 'round',
    zIndex: 50,
    })
    
    map.add(polyline);
    }
    path_markMap()
    '''
    path_str = ""
    for i in range(len(marker_list)):
        if i == len(marker_list):
            path_str = path_str + '[' + str(marker_list[i]) + ']'
        else:
            path_str = path_str + '[' + str(marker_list[i]) + '],'
    
    path_str = '[' + path_str + ']'

    path_markMap_JS_str = path_markMap_JS_str.replace("marker_list",path_str)
    return path_markMap_JS_str

def roboFlash_JS(lon_lat):
    roboFlash_JS_str = '''
    marker.setPosition([lon_lat]); 
    '''
    roboFlash_JS_str = roboFlash_JS_str.replace("lon_lat",lon_lat)
    return roboFlash_JS_str

def roboPathFlash_JS(lon_lat_waypoint):
    roboPathFlash_JS_str = '''
    function robo_path_markMap(){
    var robo_path = lon_lat_waypoint;
    var polyline_robo = new AMap.Polyline({
    path: robo_path,
    isOutline: false,
    borderWeight: 1,
    strokeColor: "#FF0000",
    strokeOpacity: 1,
    strokeWeight: 2,
    strokeStyle: "solid",
    strokeDasharray: [10, 5],
    lineJoin: 'round',
    lineCap: 'round',
    zIndex: 50,
    })
    
    map.add(polyline_robo);
    }
    robo_path_markMap()
    '''
    
    robo_path_str = '[['+str(lon_lat_waypoint[0])+'],['+ str(lon_lat_waypoint[1])+']]'
    

    roboPathFlash_JS_str = roboPathFlash_JS_str.replace("lon_lat_waypoint",str(robo_path_str))
    
    
    return roboPathFlash_JS_str