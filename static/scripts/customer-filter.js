function toPersianNum( num, dontTrim ) {

    var i = 0,

        dontTrim = dontTrim || false,

        num = dontTrim ? num.toString() : num.toString().trim(),
        len = num.length,

        res = '',
        pos,

        persianNumbers = typeof persianNumber == 'undefined' ?
            ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'] :
            persianNumbers;

    for (; i < len; i++)
        if (( pos = persianNumbers[num.charAt(i)] ))
            res += pos;
        else
            res += num.charAt(i);

    return res;
}

$(document).ready(function() {
    $('.form-check-input').on('change', function() {
        let selectedCategories = [];
        
        $('.form-check-input:checked').each(function() {
            selectedCategories.push($(this).val());
            
        });

        if (selectedCategories.length == 0){
            filterCustomer("None")
        }
        else{
            filterCustomer(selectedCategories)
        }
        
    })
})

function filterCustomer(selectedCategories){
    $.ajax({
        url: "/",
        data: {
            'filter':3,
            'categories[]': selectedCategories
        },
        success: function(data) {
            data = data['data']
            console.log(data)
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
                  <td class="email align-middle white-space-nowrap"><a href="/${data[i].id}/customer" class="fw-semi-bold ">${toPersianNum(data[i].phone_number)}</a></td>
                  <td class="mobile_number align-middle white-space-nowrap"><a class="fw-bold text-1100" href="">${data[i].address}</a></td>
                  <td class="city align-middle white-space-nowrap text-2000 fw-semi-bold">${data[i].active_credit === false ? '<span class="badge badge-phoenix badge-phoenix-success">تسویه شده</span>' :'<span class="badge badge-phoenix badge-phoenix-danger"> تسویه نشده</span>' }</td>
                  <td class="last_active align-middle text-end white-space-nowrap text-2000 fw-semi-bold">${toPersianNum(data[i].joined).replace(/-/g, '/')}</td>
                  
                </tr>    
                
            ` 
        }
        document.getElementById('members-table-body').innerHTML = ""
        document.getElementById('customer-table').innerHTML = html
            
        }
    });
}
