function ipv4hexconv(item, i, arr) {
    if (i==0){
      arr = arr + parseInt(item, 16);
    }else{
      arr = arr + '.' + parseInt(item, 16);
      }
    //Редачим формат ipv4
  }
  
  function ipv6hexconv(item, i, arr) {
    if (i==0){
       if ((item=="00" && arr[i+1]=="00") || (item!=="00")){
         resultip = resultip + item;
       }
    }else if(i%2==0){
      if ((item=="00" && arr[i+1]=="00") || (item!=="00")){
        resultip = resultip + ":" + item.replace(/0(.*[^0])/,'$1');
      }else{resultip = resultip + ":";}
    }else{
      if ((arr[i-1]=="00") && (item!=="00")){
        resultip = resultip + item.replace(/0(.*[^0])/,'$1');
      }else{
        resultip = resultip + item;
      }
    }
    return resultip;
  }
  
  function ipv6format(item, i, octeti) {
    if (item=="0000"){
      if (end_one==0){
        if (octeti[i+1]=="0000"){
          start=start+1;
        }else{
          final = final + "::";
          start = 0;
          end_one = 1;
          end = 1;
        }
      }else{
        final = final + ":0";
      }
    }else{
       if (i==0){
         final = final + item;
       }else if (end==1){
         final = final + item;
         end=0
       }else{
          final = final + ":" + item;
        }
    }
    return final;
  }
  
  function lld_obj_add(lld_one, index, lld_obj, lld_obj_ip) {
    if (lld_one.sessaddr) {
      //Берем ip из json
      lld_obj_ip = lld_one.sessaddr;
      if(lld_obj_ip.indexOf('"') == -1){
        //arr = lld_obj_ip.split(" ");
        //Массив для промежуточного формата ip.
        resultip = lld_obj_ip.split(" ");
        //Массив для конечного ip.
        finalip = '';
        start = 0;
        end = 0;
        end_one = 0;
  
        if (lld_one.addrtype){
          if (lld_one.addrtype == 2){
            //Для ipv6
            //resultip = arr.forEach(ipv6hexconv);
            //octeti = resultip.split(":");
            //final = octeti.forEach(ipv6format);
            //finalip = resultip;
            //final_json = '';
            //lld_one.sessaddr = final;
            finalip = 'IPV6'
          }else{
            //Для ipv4
            resultip.forEach(ipv4hexconv);
            finalip = resultip;
            lld_one.sessaddr = finalip;
          }
        }
      }
    }
  }
  
  lld_obj_ip = '';
  lld_obj = JSON.parse(value);
  
  lld_obj.forEach(lld_obj_add);
  //return JSON.stringify(lld_obj);
  return JSON.stringify(lld_obj);