function find_customer(search){
    
    $.ajax({
        type:"GET",
        url:"/",
        dataType:'json',
        data:{
            name: search,
            search_type: search.startsWith("0") ? 'phone_number' : 'full_name',
            
        },
      
        success: function(data) {
            data = data['data']
            var html = ""
            for(var i = 0 ; i < data.length; i++){
                html += `
                
                <tr class="hover-actions-trigger btn-reveal-trigger position-static">
                      <td class="customer align-middle white-space-nowrap"><a class="d-flex align-items-center text-900 text-hover-1000" href="#!">
                          <div class="avatar avatar-m">
                            <div class="avatar-name rounded-circle"><span>R</span></div>
                          </div>
                          <h6 class="mb-0 ms-3 fw-semi-bold">${data[i].full_name}</h6>
                        </a></td>
                      <td class="email align-middle white-space-nowrap"><a class="fw-semi-bold ">${data[i].phone_number}</a></td>
                      <td class="mobile_number align-middle white-space-nowrap"><a class="fw-bold text-1100" href="">${data[i].address}</a></td>
                      <td class="city align-middle white-space-nowrap text-2000 fw-semi-bold">${data[i].active_credit === false ? '<span class="badge badge-phoenix badge-phoenix-success">تسویه شده</span>' :'<span class="badge badge-phoenix badge-phoenix-danger"> تسویه نشده</span>' }</td>
                      <td class="last_active align-middle text-end white-space-nowrap text-2000 fw-semi-bold">${data[i].joined}</td>
                      <td class="joined align-middle white-space-nowrap text-2000 text-end fw-semi-bold"><button class="btn btn-danger">حذف</button></td>
                    </tr>    
                    
                ` 
            }
            
            document.getElementById('customer-table').innerHTML = html
        }
        
    })
}


document.getElementById('search-customer').addEventListener('input', ()=>{
    
    var search = document.getElementById('search-customer').value
    find_customer(search)

}
)

document.getElementById('search-customer').addEventListener('input', ()=>{
    document.getElementById('members-table-body').innerHTML = ""
})