import { useState, useEffect } from "react"
import React from 'react'

function App() {

  const [data, setData] =  useState([{}])

  useEffect(() => {
    fetch("/").then(
      res => res.json()
    ).then(
      data => {
        setData(data)
        console.log(data)
      }
    )
  }, [])

  return (
    <div>
        
    </div>
  )
}

export default App
