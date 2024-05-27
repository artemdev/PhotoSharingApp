import AuthMenu from './AuthMenu'
import UserMenu from './UserMenu'
import Navbar from 'react-bootstrap/Navbar'
import Container from 'react-bootstrap/Container'

export default function NavBar() {
    const isLoggedIn = sessionStorage.getItem('currentUser')

    return (
        <Navbar>
            <Container className="p-0">
                <Navbar.Brand href="/">PhotoSharing app</Navbar.Brand>
                <Navbar.Collapse className="justify-content-end">
                    {isLoggedIn ? <UserMenu /> : <AuthMenu />}
                </Navbar.Collapse>
            </Container>
        </Navbar>
    )
}
