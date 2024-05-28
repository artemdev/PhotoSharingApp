import { Formik } from 'formik'
import * as yup from 'yup'
import { Button, Form } from 'react-bootstrap'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import ROUTES from '../../routes'
export default function AddPhoto() {
   
    const navigate = useNavigate()
    const validationSchema = yup.object().shape({
        file: yup.mixed().required(),
        description: yup.string(),
        tags: yup.string(),
    })

    const initialValues = {
        file: undefined,
        description: '',
        tags: '',
    }

    const handleAddPhoto = async (values) => {
        const formData = new FormData()
        formData.append('file', values.file)
        formData.append('description', values.description)
        formData.append('tags', values.tags)
        const config = {
            headers: {
                Accept: 'application/json',
                Authorization: `Bearer ${
                    JSON.parse(sessionStorage.getItem('currentUser'))
                        .access_token
                }`,
                'Content-Type': 'multipart/form-data',
            },
        }
        try {
            await axios.post('/photos/', formData, config)
            navigate(ROUTES.PHOTO_LIBRARY)
        } catch (error) {
            alert(error.message)
        }
    }

    return (
        <Formik
            validationSchema={validationSchema}
            onSubmit={handleAddPhoto}
            initialValues={initialValues}
        >
            {({ handleSubmit, setFieldValue, values }) => (
                <Form onSubmit={handleSubmit}>
                    <Form.Group className="mb-3">
                        <Form.Label>File</Form.Label>
                        <Form.Control
                            type="file"
                            onChange={(event) => {
                                setFieldValue(
                                    'file',
                                    event.currentTarget.files[0]
                                )
                            }}
                            isInvalid={!!values.file}
                        />
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label>Description</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="Description"
                            name="description"
                            onChange={(event) => {
                                setFieldValue('description', event.target.value)
                            }}
                            value={values.description}
                        />
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Tags</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="Tags"
                            name="tags"
                            onChange={(event) => {
                                setFieldValue('tags', event.target.value)
                            }}
                            value={values.tags}
                        />
                    </Form.Group>

                    <Button type="submit" variant="primary">
                        Add Photo
                    </Button>
                </Form>
            )}
        </Formik>
    )
}
