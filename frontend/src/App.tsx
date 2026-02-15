import { useEffect } from 'react'
import ChatInterface from './components/ChatInterface'

function App() {
    // Apply Inter font
    useEffect(() => {
        document.body.style.fontFamily = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif"
    }, [])

    return (
        <ChatInterface />
    )
}

export default App
