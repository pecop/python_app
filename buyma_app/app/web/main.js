"use strict"

let items = []
const fetch_tbody = $('#fetch-tbody')


class Item {
    constructor(id, name, price, access, like, category1, category2, category3) {
        this.id = id
        this.name = name
        this.price = price
        this.access = access
        this.like = like
        this.category1 = category1
        this.category2 = category2
        this.category3 = category3
    }

    view() {

        const tr = $('<tr>')
        const td_id = $('<td>').text(this.id)
        const td_name = $('<td>').text(this.name).addClass('abridgement')
        const td_price = $('<td>').text(this.price)
        const td_access = $('<td>').text(this.access)
        const td_like = $('<td>').text(this.like)

        tr.append(td_id).append(td_name).append(td_price).append(td_access).append(td_like)
        fetch_tbody.append(tr)

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
    alert('Seleniumドライバ設定中・・・', 'warning')
    eel.search(searchInfo)

})

$('#fetch').click(() => {

    const fetchNumber = Number($('#fetch-number').val())
    alert('情報取得中・・・', 'warning')
    eel.fetch(fetchNumber)

})

$('#save').click(() => {

    const fileName = $('#file-name').val()
    eel.save(fileName)

})

const alert = (message, message_color) => {

    const alert = $('<div>').text(message).addClass(`alert alert-${message_color} vanish`).attr('role', 'alert').hide()
    $('#message').empty()
    $('#message').append(alert)
    alert.fadeIn(500)
}


eel.expose(fetch_enable)
function fetch_enable() {
    $('#fetch').prop('disabled', false)
}

eel.expose(save_enable)
function save_enable() {
    $('#save').prop('disabled', false)
}

eel.expose(message)
function message(message, isError=false, isWarning=false) {

    let message_color

    if (isError) {
        message_color = 'danger'
        console.error(message)
    } else if (isWarning) {
        message_color = 'warning'
        console.log(message)
    } else {
        message_color = 'success'
        console.log(message)
    }

    alert(message, message_color)

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

    fetch_tbody.empty()

    items.forEach(item => {
        item.view()
    })

}


$('body').on('click', '.vanish', function() {
    $(this).remove()
})

