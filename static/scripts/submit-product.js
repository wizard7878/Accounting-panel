function submit_product(url, data){
    
    $.ajax({
        type:"POST",
        url: url,
        dataType:'json',
        data:{
            data: data,
            name: "submit-product"
            
        },
      
        success: function(data) {
            data = data['data']
            var html = ""
            console.log(data)
            
           
        }
        
    })
}