import Navbar from 'react-bootstrap/Navbar'

import SignUpModal from './SignUpModal'
import LogInModal from './LogInModal'

export default function AuthMenu() {
    return (
        <>
            <Navbar.Text className="me-2">
                <SignUpModal />
            </Navbar.Text>

            <Navbar.Text>
                <LogInModal />
            </Navbar.Text>
        </>
    )
}
