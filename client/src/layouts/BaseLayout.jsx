import NavBar from '../components/NavBar'

export default function BaseLayout({ children }) {
    return (
        <>
            <NavBar />
            {children}
        </>
    )
}
