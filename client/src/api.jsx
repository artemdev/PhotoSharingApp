import axios from 'axios'

import GAMES_DB from './db'

axios.defaults.baseURL = 'http://localhost:3001'

const axiosWithToken = axios.create({
    headers: {
        Authorization: `Bearer ${
            JSON.parse(sessionStorage.getItem('currentUser'))?.token
        }`,
    },
})

export const getAllGames = () => {
    return GAMES_DB
}

export const getGameById = (id) => GAMES_DB.find((game) => game.id === id)

export const getGameBalance = async (gameId) => {
    try {
        const {
            data: { data },
        } = await axiosWithToken.post('/gameBalance')

        return data.balance
    } catch (error) {
        console.log('error', error)
    }
}

export const updateBalance = async (amount) => {
    try {
        const {
            data: { data },
        } = await axiosWithToken.put('/gameBalance', { amount })

        return data.balance
    } catch (error) {
        console.log('error', error)
    }
}

export const getGamesByName = (name) =>
    GAMES_DB.filter((game) => game.name.includes(name))

export const signUp = async (user) => {
    try {
        const response = await axios.post('/auth/signup', user)

        sessionStorage.setItem(
            'currentUser',
            JSON.stringify(response.data.data)
        )

        window.location.reload()
    } catch (error) {
        alert(error.response.data.message)
    }
}

export const signIn = async (user) => {
    try {
        const response = await axios.post('/auth/login', user)

        sessionStorage.setItem(
            'currentUser',
            JSON.stringify(response.data.data)
        )

        window.location.reload()
    } catch (error) {
        alert(error.response.data.message)
    }
}

export const signOut = async () => {
    try {
        await axiosWithToken.post('/auth/logout')

        sessionStorage.removeItem('currentUser')

        window.location.reload()
    } catch (error) {
        alert(error.response.data.message)
    }
}
