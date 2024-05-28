import React from 'react'
import { Card, Container, Row, Col } from 'react-bootstrap'
import PHOTOS_DB from '../../db'
import { useNavigate } from 'react-router-dom'
import ROUTES from '../../routes'

export default function PhotoLibrary() {
    const navigate = useNavigate()
    const openPhoto = (id) => {
        navigate(ROUTES.PHOTO.replace(':id', id))
    }

    return (
        <Container>
            <Row>
                {PHOTOS_DB.map((game) => (
                    <Col sm={4} key={game.id}>
                        <Card onClick={() => openPhoto(game.id)}>
                            <Card.Img variant="top" src={game.image_url} />
                            <Card.Body>
                                <Card.Text>{game.description}</Card.Text>
                            </Card.Body>
                        </Card>
                    </Col>
                ))}
            </Row>
        </Container>
    )
}
