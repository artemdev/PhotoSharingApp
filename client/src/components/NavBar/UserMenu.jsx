import Navbar from 'react-bootstrap/Navbar'

import { signOut } from '../../api'
import { Button } from 'react-bootstrap'

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
                <Button variant="success">Your photos</Button>
            </Navbar.Text>
            <Navbar.Text>
                <Button onClick={handleSignOut}>Logout</Button>
            </Navbar.Text>
        </>
    )
}
