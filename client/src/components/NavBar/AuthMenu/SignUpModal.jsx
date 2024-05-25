import { useState } from 'react'
import { Formik } from 'formik'
import * as yup from 'yup'
import moment from 'moment'
import { Button, Form, Row, Col, Modal } from 'react-bootstrap'

import ShowPasswordIcon from '../../common/PasswordVisibilityIcon'

import { signUp } from '../../../api'

const TITLE = 'Sign up'

export default function SignInForm({ handleClose }) {
    const [showPassword, setShowPassword] = useState(false)
    const [showModal, setShowModal] = useState(false)

    const validationSchema = yup.object().shape({
        password: yup
            .string()
            .nullable()
            .matches(
                /^(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[@$!%*?&])([a-zA-Z0-9@$!%*?&]{5,})$/,
                'Password should have at least 5 digits, 1 special char, 1 number, one letter.'
            )
            .required(),

        passwordConfirmation: yup
            .string()
            .oneOf([yup.ref('password'), null], 'Passwords must match')
            .required(),

        birthday: yup
            .date()
            .nullable()
            .test(
                'birthday',
                'Should be greater than 18',
                function (value, ctx) {
                    const dob = new Date(value)
                    const validDate = new Date()
                    const valid =
                        validDate.getFullYear() - dob.getFullYear() >= 18
                    return !valid ? ctx.createError() : valid
                }
            )
            .required(),
    })

    const initialValues = {
        username: 'Gamer',
        password: 'Gamer123$',
        passwordConfirmation: 'Gamer123$',
        birthday: moment()
            .subtract(18, 'years')
            .format('YYYY-MM-DD')
            .toString(),
    }

    const handleSignUp = async ({ username, password, birthday }) => {
        const result = await signUp({ username, password, birthday })
        if (result) {
            setShowModal(false)
        }
    }

    return (
        <>
            <Button variant="primary" onClick={() => setShowModal(true)}>
                {TITLE}
            </Button>

            <Modal show={showModal} onHide={() => setShowModal(false)}>
                <Modal.Header closeButton>
                    <Modal.Title>{TITLE}</Modal.Title>
                </Modal.Header>

                <Formik
                    validationSchema={validationSchema}
                    onSubmit={handleSignUp}
                    initialValues={initialValues}
                >
                    {({
                        handleSubmit,
                        handleChange,
                        validateForm,
                        values,
                        errors,
                    }) => (
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

                                    <Col sm={9}>
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
                                            isInvalid={!!errors.password}
                                            onChange={handleChange}
                                            value={values.password}
                                        />

                                        <Form.Control.Feedback type="invalid">
                                            {errors.password}
                                        </Form.Control.Feedback>
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

                                <Form.Group
                                    as={Row}
                                    className="mb-3"
                                    controlId="passwordConfirmation"
                                >
                                    <Form.Label column sm={3}>
                                        Password confirmation
                                    </Form.Label>

                                    <Col sm={8} className="pe-0">
                                        <Form.Control
                                            type={
                                                showPassword
                                                    ? 'text'
                                                    : 'password'
                                            }
                                            value={values.passwordConfirmation}
                                            name="passwordConfirmation"
                                            placeholder="Password confirmation"
                                            isInvalid={
                                                !!errors.passwordConfirmation
                                            }
                                            onChange={handleChange}
                                        />

                                        <Form.Control.Feedback type="invalid">
                                            {errors.passwordConfirmation}
                                        </Form.Control.Feedback>
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

                                <Form.Group
                                    as={Row}
                                    className="mb-3"
                                    controlId="birthday"
                                >
                                    <Form.Label column sm={3}>
                                        Birthday
                                    </Form.Label>

                                    <Col sm={9}>
                                        <Form.Control
                                            type="date"
                                            value={values.birthday}
                                            name="birthday"
                                            placeholder="Birthday"
                                            isInvalid={!!errors.birthday}
                                            onChange={handleChange}
                                        />

                                        <Form.Control.Feedback type="invalid">
                                            {errors.birthday}
                                        </Form.Control.Feedback>
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

                                <Button
                                    type="submit"
                                    variant="primary"
                                    onClick={validateForm}
                                >
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
