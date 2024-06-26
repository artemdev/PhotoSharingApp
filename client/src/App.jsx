import { Routes, Route } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import Container from 'react-bootstrap/Container'

import PrivateRoute from './components/Router/PrivateRoute'
import PublicRoute from './components/Router/PublicRoute'
import ROUTES from './routes'

import MainPage from './components/MainPage'
import PhotoLibrary from './components/Photos/PhotoLibrary'
import AddPhoto from './components/Photos/AddPhoto'
import ShowPhoto from './components/Photos/ShowPhoto'
import Login from './components/Login'
import SignUp from './components/MainPage'

import NavBar from './components/NavBar'
import Loader from './components/Loader'

import 'bootstrap/dist/css/bootstrap.css'

export default function App() {
    return (
        <div className="body-bg">
            <Container>
                <NavBar />
                <Suspense fallback={<Loader />}>
                    <Routes>
                        <Route
                            path={ROUTES.MAIN_PAGE}
                            element={withPublicRoute(<MainPage />, {
                                restricted: true,
                            })}
                        />

                        <Route
                            path={ROUTES.ADD_PHOTO}
                            element={withPrivateRoute(<AddPhoto />)}
                        />

                        <Route
                            path={ROUTES.PHOTO}
                            element={withPrivateRoute(<ShowPhoto />)}
                        />

                        <Route
                            path={ROUTES.PHOTO_LIBRARY}
                            element={withPrivateRoute(<PhotoLibrary />)}
                        />

                        <Route
                            path={ROUTES.LOGIN}
                            element={withPrivateRoute(<Login />)}
                        />
                        <Route
                            path={ROUTES.SIGNUP}
                            element={withPrivateRoute(<SignUp />)}
                        />
                    </Routes>
                </Suspense>
            </Container>
        </div>
    )
}

function withPrivateRoute(children, routeProps = {}) {
    return <PrivateRoute {...routeProps}>{children}</PrivateRoute>
}

function withPublicRoute(children, routeProps = {}) {
    return <PublicRoute {...routeProps}>{children}</PublicRoute>
}
