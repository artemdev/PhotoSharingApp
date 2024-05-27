import { Navigate } from 'react-router-dom'

import ROUTES from '../../routes'

export default function PrivateRoute({
    children,
    redirectTo = ROUTES.MAIN_PAGE,
    ...routeProps
}) {
    const isLoggedIn = sessionStorage.getItem('currentUser')

    return isLoggedIn ? children : <Navigate to={redirectTo} />
}
