export const getId = (url) => {
    const arr = url.split('/')
    if (arr[arr.length - 1]) {
        return arr[arr.length - 1];
    }
    return arr[arr.length - 2];
}
