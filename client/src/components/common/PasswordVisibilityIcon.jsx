// import { ReactComponent as PasswordVisible } from '../../assets/passwordVisible.svg'
// import { ReactComponent as PasswordHidden } from '../../assets/passwordHidden.svg'

export default function PasswordVisibilityIcon({
    showPassword,
    setShowPassword,
}) {
    const toggleShowPassword = () => setShowPassword(!showPassword)

    return (
        <>
            {showPassword ? (
                <div onClick={toggleShowPassword}> Show pass</div>
            ) : (
                <div onClick={toggleShowPassword}> Hide pass</div>

                // <PasswordHidden onClick={toggleShowPassword} />
            )}
        </>
    )
}
