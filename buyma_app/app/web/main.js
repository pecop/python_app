"use strict"

let items = []
const fetch_tbody = document.getElementById('fetch-tbody')

class Item {
    constructor(id, name, price, access, like, category1, category2, category3) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.access = access;
        this.like = like;
        this.category1 = category1;
        this.category2 = category2;
        this.category3 = category3;
    }

    view() {

        const tr = document.createElement('tr');
        const td_id = document.createElement('td');
        const td_name = document.createElement('td');
        const td_price = document.createElement('td');
        const td_access = document.createElement('td');
        const td_like = document.createElement('td');
        const td_category1 = document.createElement('td');
        const td_category2 = document.createElement('td');
        const td_category3 = document.createElement('td');

        td_id.textContent = this.id;
        td_name.textContent = this.name;
        td_price.textContent = this.price;
        td_access.textContent = this.access;
        td_like.textContent = this.like;
        td_category1.textContent = this.category1;
        td_category2.textContent = this.category2;
        td_category3.textContent = this.category3;

        tr.appendChild(td_id);
        tr.appendChild(td_name);
        tr.appendChild(td_price);
        tr.appendChild(td_access);
        tr.appendChild(td_like);
        tr.appendChild(td_category1);
        tr.appendChild(td_category2);
        tr.appendChild(td_category3);
        fetch_tbody.appendChild(tr);
    }
}

$('#search').click(() => {

    const keyword = $('#keyword').val()
    const isSale = $('#isSale').prop('checked')
    const priceLower = $('#price-lower').val()
    const priceUpper = $('#price-upper').val()

    const searchInfo = {
        keyword: keyword,
        isSale: isSale,
        priceLower: priceLower,
        priceUpper: priceUpper,
    }

    eel.search(searchInfo)

})

$('#fetch').click(() => {

    const fetchNumber = Number($('#fetch-number').val())
    eel.fetch(fetchNumber)

})

$('#save').click(() => {

    const fileName = $('#file-name').val()
    eel.save(fileName)

})

eel.expose(fetch_enable)
function fetch_enable() {
    $('#fetch').prop('disabled', false)
}

eel.expose(save_enable)
function save_enable() {
    $('#save').prop('disabled', false)
}

eel.expose(message)
function message(message, isError=false) {

    let message_color

    if (isError) {
        message_color = 'danger'
        console.error(message)
    } else {
        message_color = 'success'
        console.log(message)
    }

    const alert = $('<div>').text(message).addClass(`alert alert-${message_color} vanish`).attr('role', 'alert').hide()
    $('#message').empty()
    $('#message').append(alert)
    alert.fadeIn(500)

}


const clearTableView = () => {

    const trNodes = document.querySelectorAll('#fetch-tbody>tr')
    console.log(trNodes.length)

    if (trNodes) {
        trNodes.forEach(trNode => {
            console.log(trNode)
            fetch_tbody.removeChild(trNode)
        })
    }
}

eel.expose(viewInfo)
function viewInfo(item_info) {

    items = []
    const keys = Object.keys(item_info)
    const fetchNumber = item_info[keys[0]].length
    const formatter = new Intl.NumberFormat('ja', {
        style: 'currency',
        currency: 'JPY'  
      })

    for (let i = 0; i < fetchNumber; i++) {
        const name = item_info.name[i]
        const price = formatter.format(item_info.price[i])
        const access = item_info.access[i]
        const like = item_info.like[i]
        const category1 = item_info.category1[i]
        const category2 = item_info.category2[i]
        const category3 = item_info.category3[i]
        items.push(new Item(i+1, name, price, access, like, category1, category2, category3))
    }

    clearTableView()

    items.forEach(item => {
        item.view();
    })

}


$('body').on('click', '.vanish', function() {
    $(this).remove();
});

