import { useState } from 'react'
import { Formik } from 'formik'
import { Button, Form, Row, Col, Modal } from 'react-bootstrap'

import { signIn } from '../../../api'
import ShowPasswordIcon from '../../common/PasswordVisibilityIcon'

const TITLE = 'Log in'

export default function LogInModal() {
    const [showPassword, setShowPassword] = useState(false)
    const [showModal, setShowModal] = useState(false)

    const initialValues = { username: '', password: '' }

    const handleLogIn = async ({ username, password }) => {
        try {
            const user = await signIn({ username, password })

            if (user) {
                setShowModal(false)
            }
        } catch (error) {
            console.log(error)
        }
    }

    return (
        <>
            <Button variant="success" onClick={() => setShowModal(true)}>
                {TITLE}
            </Button>

            <Modal show={showModal} onHide={() => setShowModal(false)}>
                <Modal.Header closeButton>
                    <Modal.Title>{TITLE}</Modal.Title>
                </Modal.Header>

                <Formik onSubmit={handleLogIn} initialValues={initialValues}>
                    {({ handleSubmit, handleChange, values }) => (
                        <Form onSubmit={handleSubmit}>
                            <Modal.Body>
                                <Form.Group
                                    as={Row}
                                    className="mb-3"
                                    controlId="username"
                                >
                                    <Form.Label column sm={3}>
                                        Username
                                    </Form.Label>

                                    <Col sm={8} className="pe-0">
                                        <Form.Control
                                            type="input"
                                            placeholder="Username"
                                            name="username"
                                            onChange={handleChange}
                                            value={values.username}
                                        />
                                    </Col>
                                </Form.Group>

                                <Form.Group
                                    as={Row}
                                    className="mb-3"
                                    controlId="password"
                                >
                                    <Form.Label column sm={3}>
                                        Password
                                    </Form.Label>

                                    <Col sm={8} className="pe-0">
                                        <Form.Control
                                            type={
                                                showPassword
                                                    ? 'text'
                                                    : 'password'
                                            }
                                            placeholder="Password"
                                            name="password"
                                            onChange={handleChange}
                                            value={values.password}
                                        />
                                    </Col>

                                    <Col sm={1}>
                                        <ShowPasswordIcon
                                            {...{
                                                setShowPassword,
                                                showPassword,
                                            }}
                                        />
                                    </Col>
                                </Form.Group>
                            </Modal.Body>

                            <Modal.Footer>
                                <Button
                                    variant="secondary"
                                    onClick={() => setShowModal(false)}
                                >
                                    Close
                                </Button>

                                <Button type="submit" variant="primary">
                                    {TITLE}
                                </Button>
                            </Modal.Footer>
                        </Form>
                    )}
                </Formik>
            </Modal>
        </>
    )
}
