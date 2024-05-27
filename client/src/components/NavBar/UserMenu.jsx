import Navbar from 'react-bootstrap/Navbar'

import { signOut } from '../../api'
import { Button } from 'react-bootstrap'
import { Link } from 'react-router-dom'

import ROUTES from '../../routes'

export default function UserMenu() {
    const username = JSON.parse(sessionStorage.getItem('currentUser'))?.username

    const handleSignOut = async (e) => {
        e.preventDefault()
        await signOut()
    }

    return (
        <>
            <Navbar.Text className="me-2">Hi, {username}</Navbar.Text>

            <Navbar.Text className="me-2">
                <Button variant="success" className="me-2">
                    Your photos
                </Button>
                <Button as={Link} to={ROUTES.ADD_PHOTO} variant="success">
                    Add photo
                </Button>
            </Navbar.Text>
            <Navbar.Text>
                <Button onClick={handleSignOut}>Logout</Button>
            </Navbar.Text>
        </>
    )
}
