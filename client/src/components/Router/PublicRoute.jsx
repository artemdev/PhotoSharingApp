import { Navigate } from 'react-router-dom'

import ROUTES from '../../routes'

export default function PublicRoute({
    children,
    redirectTo = ROUTES.PHOTOS_LIBRARY,
    restricted = false,
    ...routeProps
}) {
    const isLoggedIn = sessionStorage.getItem('currentUser')
    const shouldRedirect = restricted && isLoggedIn

    return shouldRedirect ? <Navigate to={redirectTo} /> : children
}
