import React from 'react'
import { useParams } from 'react-router-dom'
import { Card, Container } from 'react-bootstrap'
import PHOTOS_DB from '../../db'

export default function ShowPhoto() {
    const { id } = useParams()
    const game = PHOTOS_DB.find((game) => game.id === Number(id))

    if (!game) {
        return <div>Photo not found</div>
    }

    return (
        <Container>
            <Card>
                <Card.Img variant="top" src={game.image_url} />
                <Card.Body>
                    <Card.Text>{game.description}</Card.Text>
                </Card.Body>
            </Card>
        </Container>
    )
}
