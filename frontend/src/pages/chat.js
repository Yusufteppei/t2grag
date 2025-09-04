import React, { useState } from 'react';
import axios from 'axios';
import { useEffect } from 'react';
import { URL } from '@/env_vars';


const ChatInterface = () => {
  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [ chat, setChat] = useState(null)

  // Function to fetch chat
  const fetchChat = async () => {

    try{
      // Make POST request to the backend
      const response = await axios.get(`${URL}/get_chat`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      var messages = response.data.messages
      console.log(response)
      setChat(response.data)
      setMessages(messages)
    }
    catch(error){
      console.log(error)
    }
    finally {

    }
    
  }

  // Function to handle user input submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (userInput.trim() === '') {
      return; // Avoid empty submissions
    }

    // Add user message to the chat
    setMessages((prevMessages) => [
      ...prevMessages,
      { role: 'user', content: userInput },
    ]);

    setLoading(true);

    try {
      // Make POST request to the backend
      const response = await axios.post('http://localhost:8000/answer', 
        {
          query: userInput, messages: messages, chat_id: 1
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      // Add backend response to the chat
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: 'assistant', content: response.data.answer },
      ]);
      
    } catch (error) {
      // Handle error if request fails
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: 'assistant', content: 'Sorry, something went wrong.' },
      ]);
    } finally {
      setLoading(false);
      setUserInput(''); // Clear input field after submission
    }
  };


  useEffect(() => {
    fetchChat()
  }, [])
  return (
    <div className="max-w-xl mx-auto p-6 bg-white rounded-lg shadow-lg mt-10 items-center">
      <h1 className="text-2xl font-semibold text-center text-gray-800 mb-6">
        Chat - {chat ? chat.created_on.toLocaleString() : 'Loading...'}
      </h1>

      {/* Chat messages display */}
      <div className="space-y-4 h-72 overflow-y-auto p-4 border border-gray-300 rounded-lg mb-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`p-2 rounded-lg px-2 py-1 my-2 ${
              message.role === 'user'
                ? 'bg-blue-300 text-blue-800 text-sm self-end user-text'
                : 'bg-gray-300 text-gray-800 text-sm self-start assistant-text'
            }`}
          >
            {message.content}
          </div>
        ))}
        {loading && (
          <div className="text-center text-gray-500 p-2">Bot is typing...</div>
        )}
      </div>

      {/* Input form */}
      <form onSubmit={handleSubmit} className="flex space-x-2">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ask a question..."
        />
        <button
          type="submit"
          disabled={loading}
          className={`px-6 py-2  font-medium rounded-lg shadow-md hover:bg-blue-600 focus:outline-none ${
            loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
          }`}
        >
          Send
        </button>
      </form>
      <div className="px-4 py-2 bg-yellow-800 shadow-md text-center">
        {/*<Link href={"/upload"} >Upload New Document</Link>*/}
      </div>
    </div>
  );
}
export default ChatInterface;
