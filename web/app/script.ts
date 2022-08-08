// ------- ApiClient helper class to work with FastApi
let config = {auth: ""}

const chat = document.getElementById("chat")
const msgList = document.getElementById("message_list")

function setConfig(configData) {
    config = configData
    config.channels = ["notifications", `chats:${config.userId}`]

    console.log("Config initialized", config)
}

class ApiClient {
    apiUrl = 'http://127.0.0.1:5080'
    getConfigUrl = '/me'
    sendMessageUrl = '/messages'
    sendEventUrl = '/events'

    async getConfig() {
        const url = this.apiUrl + this.getConfigUrl
        const response = await fetch(url, { method: 'GET' })
        const data = await response.json()
        console.log(`Config received`, data)
        return data
    }

    async sendMessage(msg) {
        const url = this.apiUrl + this.sendMessageUrl

        console.log('Sending', msg)
        const data = {text: msg}

        let headers = {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        }

        if( config.auth ) {
            headers.Authorization = `Bearer ${config.auth}`
        }

        const options = {
            method: 'POST',
            body: JSON.stringify(data),
            headers: headers,
        }

        await fetch(url, options)
    }

    async sendEvent(event) {
        const url = this.apiUrl + this.sendEventUrl

        console.log('Sending', event)
        const options = {
            method: 'POST',
            body: JSON.stringify(event),
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json'
            },
        }

        await fetch(url, options)
    }


}

// -------

const wsCentrifugoUrl = 'ws://localhost:8000/connection/websocket'

const apiClient = new ApiClient()
const centClient = new Centrifuge(wsCentrifugoUrl)

let subscriptions = {}

// Connect to Centrifugo as soon as page ready
document.addEventListener('DOMContentLoaded', async (event) => {
    const configData = await apiClient.getConfig()
    setConfig(configData)
    centClient.setToken(config.token)

    centClient.on('connect', () => {
        console.log('WebSocket connected')

        config.channels.forEach((x) => {
            console.log(`Client subscribing to «${x}»`)
            subscriptions[x] = centClient.subscribe(x, (msg) => { handle_message(x, msg) })
        })
    })

    centClient.on('disconnect', (ctx) => {
        console.log('WebSocket disconnected')
        console.log(ctx)

        apiClient.sendEvent("disconnect")
    })

    centClient.on('error', (ctx) => {
        console.log('WebSocket error')
        console.log(ctx)
    })

    centClient.connect()

    // chat.addEventListener('keydown', sendMessage);
})

function handle_message(channel, msg) {
    console.log(`${channel}:`, msg.data)

    const chat = document.getElementById("chat")
    const msgList = document.getElementById("message_list")

    if(msg.data.type == "auth") {
        msgList.innerHTML = ""
        config.auth = msg.data.data.access_token
        config.userId = msg.data.data.user_id
        const newChannel = `chats:${msg.data.data.user_id}`
        centClient.subscribe(newChannel, (msg) => { handle_message(newChannel, msg) })
    }

    if(msg.data.type == "message" || msg.data.type == "auth") {
        const datetime_value = new Date(msg.data.created_at)

        const tpl = document.getElementById(msg.data.sender)
        const newMsg = tpl.children[0].cloneNode(true)
        const content = newMsg.getElementsByClassName("chat_message__content")[0]
        const datetime = newMsg.getElementsByClassName("chat_message__date")[0]

        content.innerHTML = msg.data.message
        datetime.innerText = datetime_value.toLocaleString()
        console.log(newMsg)

        msgList.appendChild(newMsg)
        msgList.scrollTo(0, msgList.scrollHeight)
        if(msg.data.sender == "user"){
            chat.value = ""
        }
    }
    else if (msg.data.type == "typing") {
        const tpl = document.getElementById(msg.data.sender)
        let newMsg = tpl.children[0].cloneNode(true)

        const typing = document.getElementById("typing").innerHtml
        tpl.innerHTML = typing
        msgList.appendChild(newMsg)
        msgList.scrollTo(0, msgList.scrollHeight)
    }
    else {
        console.log("some other type", msg.data.type)
    }

    if(msg.data.type == "auth") {
        msg.data.data.history.forEach((msg) => {
            console.log("HISTORY", msg)
            if(msg.message.type != "message" || msg.message.message.slice(0, 5) == "\\auth" ){
                console.log("SKIP", msg.message.type)
                return
            }
            const data = {
                "data": msg.message
            }
            handle_message(channel, data)
        })
    }
}

function sendMessage(e) {
    const chat = document.getElementById("chat")
    if (chat.value != "") {
        apiClient.sendMessage(chat.value)
    }
}
